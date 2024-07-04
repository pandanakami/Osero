using Python.Runtime;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OseroTestUI
{
	public class GameState
	{

		public bool IsAiPrepare { get; set; } = false;
		public bool IsGameStart { get; set; } = false;

		public bool IsAiIsFirst { get; set; } = false;
		public bool IsPlayerTurn { get; set; } = false;
		public Osero.STATE PlayerStone => IsAiIsFirst ? Osero.STATE.WHITE : Osero.STATE.BLACK;
		public Osero.STATE AiStone => IsAiIsFirst ? Osero.STATE.BLACK : Osero.STATE.WHITE;

		public int PutStoneNum => WhiteStoneNum + BlackStoneNum;

		public int WhiteStoneNum { get; set; } = 0;
		public int BlackStoneNum { get; set; } = 0;

		public int PassCount { get; set; } = 0;
		public string PlayerStoneString => IsAiIsFirst ? "〇" : "●";
		public string AiStoneString => IsAiIsFirst ? "●" : "〇";

#pragma warning disable CS8618
		public PyInt[] AI_STATE_VALUE_FIRST;
		public PyInt[] AI_STATE_VALUE_SECOND;
#pragma warning restore CS8618

		/// <summary>
		/// 先手・後手でオセロ状態→AI向け状態に変換するテーブル
		/// Pythonスレッド内でないと作れないので関数化
		/// </summary>
		public void InitPyConstData()
		{
			AI_STATE_VALUE_FIRST = new PyInt[] { new PyInt(Osero.AI_NONE), new PyInt(Osero.AI_OTHER), new PyInt(Osero.AI_SELF) };
			AI_STATE_VALUE_SECOND = new PyInt[] { new PyInt(Osero.AI_NONE), new PyInt(Osero.AI_SELF), new PyInt(Osero.AI_OTHER) };
		}
	}
}
