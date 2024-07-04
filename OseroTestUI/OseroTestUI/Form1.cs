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
		/// �u�����ۂ��̊m��臒l
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
		/// �Ֆʏ��
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
		/// AI�����{�^���N���b�N
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
		/// �Q�[���J�n�F�v���C���[���
		/// </summary>
		/// <param name="sender"></param>
		/// <param name="e"></param>
		private void BT_GameStartFirst_Click(object sender, EventArgs e)
		{
			_GameStart(true);

		}

		/// <summary>
		/// �Q�[���J�n�F�v���C���[���
		/// </summary>
		/// <param name="sender"></param>
		/// <param name="e"></param>
		private void BT_GameStartSecond_Click(object sender, EventArgs e)
		{
			_GameStart(false);
		}

		/// <summary>
		/// �p�X�N���b�N
		/// </summary>
		/// <param name="sender"></param>
		/// <param name="e"></param>
		private void BT_Pass_Click(object sender, EventArgs e)
		{
			_OnPass();
		}

		private void OnClosing(object? sender, FormClosingEventArgs e)
		{
			// �^�X�N�̊�����ҋ@
			if(_python_task != null) {
				_oser_event.Add(new EventMessage() { request_terminate = true });
				_python_task.Wait();
				Console.WriteLine("");
			}	
		}

		/**********************************************/

		/// <summary>
		/// PyThon���C���^�X�N
		/// </summary>
		void _PythonTask()
		{
			logger.Info("Start Python Task");

			// ���z����Python�C���^�[�v���^�̃p�X��ݒ�
			string pythonHome = @"C:\workspace\ai\.venv"; // ���z���̃��[�g�f�B���N�g�����w��
			string pythonDll = @"C:\Users\seij\AppData\Local\Programs\Python\Python310\python310.dll";

			// ���ϐ���ݒ�
			Environment.SetEnvironmentVariable("PYTHONHOME", pythonHome);
			Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", pythonDll);

			// Python�G���W����������
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

				//���݂�AI�̐F
				var stone = _state.AiStone;

				//AI�v�� => 65�̊m���z��
				var aiOutput = _DoAiRequest(osero_model);

				threadState = PythonEngine.BeginAllowThreads();

				//AI���ʉ��
				//�m����ʂ���u���邩�`�F�b�N�A65�̏ꍇ�̓p�X
				var count = 0;
				foreach(var pair in aiOutput) {
					var index = pair.Key;
					var prob = pair.Value;//�m��
					var x = index % WIDTH;
					var y = index / HEIGHT;

					//�p�X����
					if((x==0 && y == HEIGHT) || prob < PROB_THRESHOLD) {
						logger.Info($"AI Pass[{count}], prob:{prob}");
						_OnPass();
						break;
					}
					//�u���锻��
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


			// Python�G���W�����V���b�g�_�E��
			PythonEngine.Shutdown();

			logger.Info("End Python Task");
		}

		/// <summary>
		/// �I�Z����AI���f�������[�h
		/// </summary>
		/// <returns></returns>
		PyObject _GetOseroModel()
		{
			PyObject osero_model;

			string model_name = "";

			// GIL (Global Interpreter Lock)���擾
			using (Py.GIL()) {
				// Python�̃p�X�ɃX�N���v�g�̃f�B���N�g����ǉ�
				dynamic sys = Py.Import("sys");
				sys.path.append(OSERO_HOME_PATH);

				// Python�̕W���o�͂����_�C���N�g
				dynamic io = Py.Import("io");
				dynamic redirect_stdout = io.StringIO();
				sys.stdout = redirect_stdout;
				sys.stderr = redirect_stdout;

				// Python�X�N���v�g���C���|�[�g
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
		/// AI�ɐ��_�v��
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


				// Python�X�N���v�g���C���|�[�g
				dynamic m = Py.Import("osero_pred");
				var result = m.pred(model, aiInput);
				// ���ʂ����X�g�Ƃ��Ď擾
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

			// Python�X�N���v�g���C���|�[�g
			dynamic testModule = Py.Import("mytest");

			// test�֐����Ăяo��
			dynamic result = testModule.hogehoge(_ToPyList(new int[] { 1, 2, 3 }));

			var resultList = new PyList(result);


			foreach (var item in resultList) {
				Console.WriteLine(item.ToString());
			}
		}

		/**********************************************/

		/// <summary>
		/// �I�Z������
		/// </summary>
		private void _InitOsero()
		{

			Invoke(() => {

				//��Ԍ�����悤��
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
		/// �Q�[���J�n
		/// </summary>
		/// <param name="is_player_first"></param>
		private void _GameStart(bool is_player_first)
		{
			logger.Info("**** Game Start ****");

			_state.IsAiIsFirst = !is_player_first;
			_state.IsGameStart = true;
			
			_state.PassCount = 0;
			

			//�{�^��������
			_SetBtnVisible(BT_GameStartFirst, false);
			_SetBtnVisible(BT_GameStartSecond, false);

			//��ԃ��Z�b�g
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

			_UpdateStoneNum();//�΂̐�������

			if (is_player_first) {
				_StartPlayerProc();
			}
			else {
				_StartAiProc();
			}
		}

		/// <summary>
		/// �Q�[���I��
		/// </summary>
		void _GameEnd()
		{
			_state.IsGameStart = false;


			//�{�^��������
			_SetBtnVisible(BT_GameStartFirst, true);
			_SetBtnVisible(BT_GameStartSecond, true);
			_SetBtnVisible(BT_Pass, false);
		}

		/// <summary>
		/// �v���C���[��������s
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		void _OnOseroClick(int x, int y)
		{
			var stone = _state.PlayerStone;

			//�u���邩���ׂ�
			var enable_put = _Osero_CheckEnablePut(x, y, stone);
			if (!enable_put) {
				return;
			}

			//�u��
			_Osero_PutStone(x, y, stone);
			logger.Info($"Player Put({x}, {y}):{_state.PlayerStoneString}");
			_PutStoneAfter();
		}

		/// <summary>
		/// �p�X
		/// </summary>
		void _OnPass()
		{
			_state.PassCount++;

			//����Ǝ�����pass������Q�[���I��
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
		/// �v���C���[�J�n
		/// </summary>
		private void _StartPlayerProc()
		{
			logger.Info("Player Turn");
			_state.IsPlayerTurn = true;
			_SetBtnEnable(BT_Pass, true);
		}

		/// <summary>
		/// AI�J�n
		/// </summary>
		private void _StartAiProc()
		{
			logger.Info("AI Turn");
			_state.IsPlayerTurn = false;
			_SetBtnEnable(BT_Pass, false);

			//AI�J�n
			_oser_event.Add(new EventMessage());
		}


		/// <summary>
		/// �Βu�����㏈��
		/// </summary>
		void _PutStoneAfter()
		{
			_UpdateStoneNum();//�΃J�E���g
			_state.PassCount = 0;//�p�X���Z�b�g

			//�Q�[���I������
			if (_state.PutStoneNum == WIDTH * HEIGHT) {
				_GameEnd();
			}

			//�Q�[�������Ȃ�v���C���[����ւ�
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
		/// �{�^����������悤�ɂ���
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
		/// �{�^����L��/�����ɂ���
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
		/// �΂̐����X�V����
		/// </summary>
		void _UpdateStoneNum()
		{
			_state.BlackStoneNum = _osero_single_array.Count(o => o.state == Osero.STATE.BLACK);
			_state.WhiteStoneNum = _osero_single_array.Count(o => o.state == Osero.STATE.WHITE);

			Invoke(() => {
				LB_BlackNum.Text = $"���F{_state.BlackStoneNum}";
				LB_WhiteNum.Text = $"�Z�F{_state.WhiteStoneNum}";
			});
		}

		/// <summary>
		/// �z���Numpy���X�g�ɕϊ�
		/// </summary>
		/// <param name="input_val"></param>
		/// <returns></returns>
		PyList _ToPyList(IEnumerable<int> input_val)
		{
			return new PyList(input_val.Select(o => new PyInt(o)).ToArray());
		}





		/**********************************************/


		/// <summary>
		/// �u���邩�`�F�b�N
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <param name="stone"></param>
		bool _Osero_CheckEnablePut(int x, int y, Osero.STATE stone)
		{
			//���ɒu����Ă���
			if(_oseros[y, x].state != Osero.STATE.OFF) {
				return false;
			}


			//�e�����ǂꂩ��ł��u����
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
		/// �΂�u��
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
		/// �Ђ�����Ԃ邩�`�F�b�N
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <param name="stone"></param>
		/// <param name="i"></param>
		/// <param name="j"></param>
		/// <returns></returns>
		private bool __Osero_CheckEnableReplace(int x, int y, Osero.STATE stone, int i, int j)
		{
			// ����
			if (i == 0 && j == 0) {
				return false;
			}

			var other_stone = stone == Osero.STATE.WHITE ? Osero.STATE.BLACK : Osero.STATE.WHITE;
			x += i;
			y += j;
			//�T���ꏊ���͈͊O�̏ꍇ�@����
			if (!(0 <= x && x < WIDTH && 0 <= y && y < HEIGHT)) {
				return false;
			}

			// �u�����ׂ�����łȂ��@����
			else if (_oseros[y, x].state != other_stone) {
				return false;
			}

			//�ȍ~��ł����肪����
			while (true) {
				x += i;
				y += j;
				// �T���ꏊ���͈͊O�̏ꍇ�@�I��
				if (!(0 <= x && x < WIDTH && 0 <= y & y < HEIGHT)) {
					return false;
				}
				// �T���ꏊ������@�p��
				if (_oseros[y, x].state == other_stone) {
					continue;
				}

				// �T���ꏊ�������@����ւ����@�I��
				if (_oseros[y, x].state == stone) {
					return true;
				}

				// �T���ꏊ���󔒁@�I��
				else {
					return false;
				}
			}
		}

		/// <summary>
		/// �Ђ�����Ԃ�(���O��enable_replace()�`�F�b�N�ς݂ł��邱��)
		/// </summary>
		/// <param name="x"></param>
		/// <param name="y"></param>
		/// <param name="stone"></param>
		/// <param name="i"></param>
		/// <param name="j"></param>
		/// <exception cref="Exception"></exception>
		private void __Osero_Replace(int x, int y, Osero.STATE stone, int i, int j)
		{
			// ����
			if (i == 0 && j == 0) {
				return;
			}

			var other_stone = stone == Osero.STATE.WHITE ? Osero.STATE.BLACK : Osero.STATE.WHITE;

			// �ȍ~��ł����肪����
			while (true) {
				x += i;
				y += j;

				// �T���ꏊ������@����ւ�
				if (_oseros[y, x].state == other_stone) {
					_oseros[y, x].state = stone;

					continue;
				}

				// �T���ꏊ�������@�I��
				else if (_oseros[y, x].state == stone) {
					return;
				}
				// �T���ꏊ���󔒁@�I��
				else {
					throw new Exception("????");
				}
			}
		}
	}
}
