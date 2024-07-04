using Microsoft.VisualBasic.ApplicationServices;
using Python.Runtime;
using System;
using System.Collections.Concurrent;
using System.Linq;
using NLog;

namespace OseroTestUI
{
	public partial class Form1 : Form
	{

		private static Logger logger = LogManager.GetCurrentClassLogger();

		const int WIDTH = 8;
		const int HEIGHT = 8;
		
		/// <summary>
		/// 置くか否かの確率閾値
		/// </summary>
		const float PROB_THRESHOLD = 0.1f;

		const string OSERO_HOME_PATH = @"C:\workspace\ai\osero\Osero";


		class EventMessage
		{
			public bool request_terminate { get; set; } = false;
		}

		bool _is_thread_running = false;

		BlockingCollection<EventMessage> _oser_event = new BlockingCollection<EventMessage>();

		GameState _state = new GameState();

		/// <summary>
		/// 盤面情報
		/// </summary>
		private Osero[,] _oseros = new Osero[HEIGHT, WIDTH];

		private Osero[] _osero_single_array;


		private Task _python_task;

		/**********************************************/


#pragma warning disable CS8618
		public Form1()
		{
			InitializeComponent();
			this.FormClosing += OnClosing;

			logger.Info("********************** START **************************");
		}

#pragma warning restore CS8618

		/// <summary>
		/// AI準備ボタンクリック
		/// </summary>
		/// <param name="sender"></param>
		/// <param name="e"></param>
		private void bt_prepare_Click(object sender, EventArgs e)
		{
			if (_is_thread_running) {
				return;
			}
			_is_thread_running = true;

			_SetBtnVisible(bt_prepare, false);


			_python_task = Task.Run(() => {
				_PythonTask();
			});
		}

		/// <summary>
		/// ゲーム開始：プレイヤー先手
		/// </summary>
		/// <param name="sender"></param>
		/// <param name="e"></param>
		private void BT_GameStartFirst_Click(object sender, EventArgs e)
		{
			_GameStart(true);

		}

		/// <summary>
		/// ゲーム開始：プレイヤー後手
		/// </summary>
		/// <param name="sender"></param>
		/// <param name="e"></param>
		private void BT_GameStartSecond_Click(object sender, EventArgs e)
		{
			_GameStart(false);
		}

		/// <summary>
		/// パスクリック
		/// </summary>
		/// <param name="sender"></param>
		/// <param name="e"></param>
		private void BT_Pass_Click(object sender, EventArgs e)
		{
			_OnPass();
		}

		private void OnClosing(object? sender, FormClosingEventArgs e)
		{
			// タスクの完了を待機
			if(_python_task != null) {
				_oser_event.Add(new EventMessage() { request_terminate = true });
				_python_task.Wait();
				Console.WriteLine("");
			}	
		}

		/**********************************************/

		/// <summary>
		/// PyThonメインタスク
		/// </summary>
		void _PythonTask()
		{
			logger.Info("Start Python Task");

			// 仮想環境のPythonインタープリタのパスを設定
			string pythonHome = @"C:\workspace\ai\.venv"; // 仮想環境のルートディレクトリを指定
			string pythonDll = @"C:\Users\seij\AppData\Local\Programs\Python\Python310\python310.dll";

			// 環境変数を設定
			Environment.SetEnvironmentVariable("PYTHONHOME", pythonHome);
			Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", pythonDll);

			// Pythonエンジンを初期化
			PythonEngine.Initialize();

			PyObject osero_model = _GetOseroModel();
			var threadState = PythonEngine.BeginAllowThreads();

			_state.IsAiPrepare = true;
			_InitOsero();


			while (true) {
				var data = _oser_event.Take();
				if (data.request_terminate) {
					break;
				}

				PythonEngine.EndAllowThreads(threadState);

				//現在のAIの色
				var stone = _state.AiStone;

				//AI要求 => 65個の確率配列
				var aiOutput = _DoAiRequest(osero_model);

				threadState = PythonEngine.BeginAllowThreads();

				//AI結果解析
				//確率上位から置けるかチェック、65の場合はパス
				var count = 0;
				foreach(var pair in aiOutput) {
					var index = pair.Key;
					var prob = pair.Value;//確率
					var x = index % WIDTH;
					var y = index / HEIGHT;

					//パス判定
					if((x==0 && y == HEIGHT) || prob < PROB_THRESHOLD) {
						logger.Info($"AI Pass[{count}], prob:{prob}");
						_OnPass();
						break;
					}
					//置ける判定
					if(_Osero_CheckEnablePut(x,y, stone)) {
						_Osero_PutStone(x,y,stone);
						logger.Info($"AI Put[{count}]({x}, {y}):{_state.AiStoneString}, prob:{prob}");
						_PutStoneAfter();

						break;
					}
					else {
						logger.Warn($"AI Put Fail[{count}]({x}, {y}), prob:{prob}");
					}
					count++;
				}
			}


			// Pythonエンジンをシャットダウン
			PythonEngine.Shutdown();

			logger.Info("End Python Task");
		}

		/// <summary>
		/// オセロのAIモデルをロード
		/// </summary>
		/// <returns></returns>
		PyObject _GetOseroModel()
		{
			PyObject osero_model;

			string model_name = "";

			// GIL (Global Interpreter Lock)を取得
			using (Py.GIL()) {
				// Pythonのパスにスクリプトのディレクトリを追加
				dynamic sys = Py.Import("sys");
				sys.path.append(OSERO_HOME_PATH);

				// Pythonの標準出力をリダイレクト
				dynamic io = Py.Import("io");
				dynamic redirect_stdout = io.StringIO();
				sys.stdout = redirect_stdout;
				sys.stderr = redirect_stdout;

				// Pythonスクリプトをインポート
				dynamic m = Py.Import("my_module.osero_model_wrap");

				osero_model = m.load_model();
				dynamic name = m.get_model_name();
				model_name = new PyString(name).ToString();
				
				_state.InitPyConstData();
			}

			logger.Info($"Get Model Complete:{model_name}");

			return osero_model;
		}

		/// <summary>
		/// AIに推論要求
		/// </summary>
		KeyValuePair<int, float>[] _DoAiRequest(PyObject model)
		{
			KeyValuePair<int, float>[] aiOutput;

			using (Py.GIL()) {
				PyList[] aiInputBase = new PyList[HEIGHT];
				for (var j = 0; j < HEIGHT; j++) {
					PyInt[] row = new PyInt[HEIGHT];
					for (var i = 0; i < WIDTH; i++) {
						row[i] = _oseros[j, i].ai_state;
					}
					aiInputBase[j] = new PyList(row);
				}

				var aiInput = new PyList(aiInputBase);


				// Pythonスクリプトをインポート
				dynamic m = Py.Import("osero_pred");
				var result = m.pred(model, aiInput);
				// 結果をリストとして取得
				var resultList = new PyList(result.As<PyList>()[0]);

				aiOutput = resultList
					.Select((o, Index) => new KeyValuePair<int, float>(Index, (float)o.As<double>()))
					.OrderByDescending(pair=>pair.Value)
					.ToArray();
			}

			logger.Info("AI Predict Complete");
			return aiOutput;
		}


		void MyTest()
		{

			// Pythonスクリプトをインポート
			dynamic testModule = Py.Import("mytest");

			// test関数を呼び出し
			dynamic result = testModule.hogehoge(_ToPyList(new int[] { 1, 2, 3 }));

			var resultList = new PyList(result);


			foreach (var item in resultList) {
				Console.WriteLine(item.ToString());
			}
		}

		/**********************************************/

		/// <summary>
		/// オセロ準備
		/// </summary>
		private void _InitOsero()
		{

			Invoke(() => {

				//状態見えるように
				_SetBtnVisible(BT_GameStartFirst, true);
				_SetBtnVisible(BT_GameStartSecond, true);
				LB_BlackNum.Visible = true;
				LB_WhiteNum.Visible = true;

				const int OFFSET_X = 64;
				const int OFFSET_Y = 64;

				for (var j = 0; j < HEIGHT; j++) {

					for (var i = 0; i < WIDTH; i++) {
						var osero = new Osero(i, j, _OnOseroClick, _state);
						osero.Location = new Point(i * 64 + OFFSET_X, j * 64 + OFFSET_Y);
						this.Controls.Add(osero);
						osero.GameReset();
						_oseros[j, i] = osero;
					}
				}

				_osero_single_array = _oseros.Cast<Osero>().ToArray();
			});

		}

		/// <summary>
		/// ゲーム開始
		/// </summary>
		/// <param name="is_player_first"></param>
		private void _GameStart(bool is_player_first)
		{
			logger.Info("**** Game Start ****");

			_state.IsAiIsFirst = !is_player_first;
			_state.IsGameStart = true;
			
			_state.PassCount = 0;
			

			//ボタン無効化
			_SetBtnVisible(BT_GameStartFirst, false);
			_SetBtnVisible(BT_GameStartSecond, false);

			//状態リセット
			foreach (var item in _oseros) {
				item.GameReset();
			}

			/*
			int[] AAA = new int[] {
				0,0,0,0,0,0,0,0,
				0,0,0,2,0,0,0,0,
				0,0,0,1,0,0,0,0,
				0,0,0,1,0,0,0,0,
				0,0,0,1,0,0,0,0,
				0,0,0,1,0,0,0,0,
				0,0,0,1,0,0,0,0,
				0,0,0,0,0,0,0,0,
			};
			for(var j = 0; j < 8; j++) {
				for(var i = 0; i < 8; i++) {
					Osero.STATE a = AAA[j*8+i] == 0 ? Osero.STATE.OFF : AAA[j * 8 + i] == 1 ? Osero.STATE.WHITE : Osero.STATE.BLACK;
					_oseros[j, i].state = a;
				}
				
			}
			*/

			_UpdateStoneNum();//石の数初期化

			if (is_player_first) {
				_StartPlayerProc();
			}
			else {
				_StartAiProc();
			}
		}

		/// <summary>
		/// ゲーム終了
		/// </summary>
		void _GameEnd()
		{
			_state.IsGameStart = false;


			//ボタン無効化
			_SetBtnVisible(BT_GameStartFirst, true);
			_SetBtnVisible(BT_GameStartSecond, true);
			_SetBtnVisible(BT_Pass, false);
		}

		/// <summary>
		/// プレイヤーが手を実行
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		void _OnOseroClick(int x, int y)
		{
			var stone = _state.PlayerStone;

			//置けるか調べる
			var enable_put = _Osero_CheckEnablePut(x, y, stone);
			if (!enable_put) {
				return;
			}

			//置く
			_Osero_PutStone(x, y, stone);
			logger.Info($"Player Put({x}, {y}):{_state.PlayerStoneString}");
			_PutStoneAfter();
		}

		/// <summary>
		/// パス
		/// </summary>
		void _OnPass()
		{
			_state.PassCount++;

			//相手と自分がpassしたらゲーム終了
			if (_state.PassCount >= 2) {
				_GameEnd();
			}
			else {
				if (_state.IsPlayerTurn) {
					_StartAiProc();
				}
				else {
					_StartPlayerProc();
				}
					
			}
		}

		/// <summary>
		/// プレイヤー開始
		/// </summary>
		private void _StartPlayerProc()
		{
			logger.Info("Player Turn");
			_state.IsPlayerTurn = true;
			_SetBtnEnable(BT_Pass, true);
		}

		/// <summary>
		/// AI開始
		/// </summary>
		private void _StartAiProc()
		{
			logger.Info("AI Turn");
			_state.IsPlayerTurn = false;
			_SetBtnEnable(BT_Pass, false);

			//AI開始
			_oser_event.Add(new EventMessage());
		}


		/// <summary>
		/// 石置いた後処理
		/// </summary>
		void _PutStoneAfter()
		{
			_UpdateStoneNum();//石カウント
			_state.PassCount = 0;//パスリセット

			//ゲーム終了判定
			if (_state.PutStoneNum == WIDTH * HEIGHT) {
				_GameEnd();
			}

			//ゲーム続くならプレイヤー入れ替え
			else {
				if (_state.IsPlayerTurn) {
					_StartAiProc();
				}
				else {
					_StartPlayerProc();
				}

			}
		}


		/**********************************************/

		/// <summary>
		/// ボタンを見えるようにする
		/// </summary>
		/// <param name="btn"></param>
		/// <param name="enable"></param>
		private void _SetBtnVisible(Button btn, bool enable)
		{
			Invoke(() => {
				btn.Visible = enable;
				btn.Enabled = enable;
			});
			
		}
		/// <summary>
		/// ボタンを有効/無効にする
		/// </summary>
		/// <param name="btn"></param>
		/// <param name="enable"></param>
		private void _SetBtnEnable(Button btn, bool enable)
		{
			Invoke(() => {
				btn.Visible = true;
				btn.Enabled = enable;
			});
		}


		/// <summary>
		/// 石の数を更新する
		/// </summary>
		void _UpdateStoneNum()
		{
			_state.BlackStoneNum = _osero_single_array.Count(o => o.state == Osero.STATE.BLACK);
			_state.WhiteStoneNum = _osero_single_array.Count(o => o.state == Osero.STATE.WHITE);

			Invoke(() => {
				LB_BlackNum.Text = $"●：{_state.BlackStoneNum}";
				LB_WhiteNum.Text = $"〇：{_state.WhiteStoneNum}";
			});
		}

		/// <summary>
		/// 配列をNumpyリストに変換
		/// </summary>
		/// <param name="input_val"></param>
		/// <returns></returns>
		PyList _ToPyList(IEnumerable<int> input_val)
		{
			return new PyList(input_val.Select(o => new PyInt(o)).ToArray());
		}





		/**********************************************/


		/// <summary>
		/// 置けるかチェック
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <param name="stone"></param>
		bool _Osero_CheckEnablePut(int x, int y, Osero.STATE stone)
		{
			//既に置かれている
			if(_oseros[y, x].state != Osero.STATE.OFF) {
				return false;
			}


			//各方向どれか一つでも置ける
			for (var j = -1; j <= 1; j++) {
				for (var i = -1; i <= 1; i++) {
					if (__Osero_CheckEnableReplace(x, y, stone, i, j)) {
						return true;
					}
				}
			}

			return false;
		}

		/// <summary>
		/// 石を置く
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <param name="user"></param>
		void _Osero_PutStone(int x, int y, Osero.STATE user)
		{
			_oseros[y, x].state = user;

			for (var j = -1; j <= 1; j++) {
				for (var i = -1; i <= 1; i++) {
					if (__Osero_CheckEnableReplace(x, y, user, i, j)) {
						__Osero_Replace(x, y, user, i, j);
					}
				}
			}
		}

		/// <summary>
		/// ひっくり返るかチェック
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <param name="stone"></param>
		/// <param name="i"></param>
		/// <param name="j"></param>
		/// <returns></returns>
		private bool __Osero_CheckEnableReplace(int x, int y, Osero.STATE stone, int i, int j)
		{
			// 無視
			if (i == 0 && j == 0) {
				return false;
			}

			var other_stone = stone == Osero.STATE.WHITE ? Osero.STATE.BLACK : Osero.STATE.WHITE;
			x += i;
			y += j;
			//探索場所が範囲外の場合　無視
			if (!(0 <= x && x < WIDTH && 0 <= y && y < HEIGHT)) {
				return false;
			}

			// 置いた隣が相手でない　無視
			else if (_oseros[y, x].state != other_stone) {
				return false;
			}

			//以降一つでも相手がある
			while (true) {
				x += i;
				y += j;
				// 探索場所が範囲外の場合　終了
				if (!(0 <= x && x < WIDTH && 0 <= y & y < HEIGHT)) {
					return false;
				}
				// 探索場所が相手　継続
				if (_oseros[y, x].state == other_stone) {
					continue;
				}

				// 探索場所が自分　入れ替えれる　終了
				if (_oseros[y, x].state == stone) {
					return true;
				}

				// 探索場所が空白　終了
				else {
					return false;
				}
			}
		}

		/// <summary>
		/// ひっくり返す(事前にenable_replace()チェック済みであること)
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <param name="stone"></param>
		/// <param name="i"></param>
		/// <param name="j"></param>
		/// <exception cref="Exception"></exception>
		private void __Osero_Replace(int x, int y, Osero.STATE stone, int i, int j)
		{
			// 無視
			if (i == 0 && j == 0) {
				return;
			}

			var other_stone = stone == Osero.STATE.WHITE ? Osero.STATE.BLACK : Osero.STATE.WHITE;

			// 以降一つでも相手がある
			while (true) {
				x += i;
				y += j;

				// 探索場所が相手　入れ替え
				if (_oseros[y, x].state == other_stone) {
					_oseros[y, x].state = stone;

					continue;
				}

				// 探索場所が自分　終了
				else if (_oseros[y, x].state == stone) {
					return;
				}
				// 探索場所が空白　終了
				else {
					throw new Exception("????");
				}
			}
		}
	}
}
