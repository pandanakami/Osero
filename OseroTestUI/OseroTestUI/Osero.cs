using Microsoft.VisualBasic.ApplicationServices;
using Python.Runtime;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace OseroTestUI
{
	public partial class Osero : UserControl
	{


		public enum STATE
		{
			OFF = 0,
			WHITE = 1,
			BLACK = 2
		}

		public const int AI_NONE = 0;
		public const int AI_SELF = 1;
		public const int AI_OTHER = 2;

		readonly string[] LABEL_STR = { "", "〇", "●" };

		/**********************************************/


		public int X { get; set; }
		public int Y { get; set; }
		public Action<int, int> onClick;

		/**********************************************/

		/// <summary>
		/// 状態：なし or 白 or 黒
		/// </summary>
		private STATE _state = STATE.OFF;

		private GameState _game_state;

		/**********************************************/

		/// <summary>
		/// AI用の状態：なし or 自石 or 他石
		/// </summary>
		public PyInt ai_state => _game_state.IsAiIsFirst ? _game_state.AI_STATE_VALUE_FIRST[(int)_state] : _game_state.AI_STATE_VALUE_SECOND[(int)_state];


		public STATE state
		{
			get => _state;
			set {
				var int_value = (int)value;

				_state = value;

				Invoke(() => {
					label.Text = LABEL_STR[int_value];
				});
			}
		}

		/**********************************************/


		public Osero(int X, int Y, Action<int,int>onClick, GameState game_state)
		{
			InitializeComponent();
			this.X = X;
			this.Y = Y;
			this.onClick = onClick;
			this._game_state = game_state;
		}

		private void Osero_Click(object sender, EventArgs e)
		{
			if (!_game_state.IsGameStart) {
				return;
			}
			if(_state != STATE.OFF) {
				return;
			}
			if (_game_state.IsPlayerTurn) {
				onClick?.Invoke(X, Y);
			}
			
		}

		/// <summary>
		/// ゲームリセット
		/// </summary>
		public void GameReset()
		{
			if ((X == 3 && Y == 3) || (X == 4 && Y == 4)) {
				state = Osero.STATE.WHITE;
			}
			else if ((X == 3 && Y == 4) || (X == 4 && Y == 3)) {
				state = Osero.STATE.BLACK;
			}
			else {
				state = STATE.OFF;
			}
		}
	}
}
