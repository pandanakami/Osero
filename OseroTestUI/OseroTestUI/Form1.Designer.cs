namespace OseroTestUI
{
	partial class Form1
	{
		/// <summary>
		///  Required designer variable.
		/// </summary>
		private System.ComponentModel.IContainer components = null;

		/// <summary>
		///  Clean up any resources being used.
		/// </summary>
		/// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
		protected override void Dispose(bool disposing)
		{
			if (disposing && (components != null)) {
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		#region Windows Form Designer generated code

		/// <summary>
		///  Required method for Designer support - do not modify
		///  the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{
			bt_prepare = new Button();
			BT_GameStartFirst = new Button();
			BT_GameStartSecond = new Button();
			BT_Pass = new Button();
			LB_BlackNum = new Label();
			LB_WhiteNum = new Label();
			SuspendLayout();
			// 
			// bt_prepare
			// 
			bt_prepare.Location = new Point(276, 575);
			bt_prepare.Name = "bt_prepare";
			bt_prepare.Size = new Size(75, 23);
			bt_prepare.TabIndex = 0;
			bt_prepare.Text = "準備";
			bt_prepare.UseVisualStyleBackColor = true;
			bt_prepare.Click += bt_prepare_Click;
			// 
			// BT_GameStartFirst
			// 
			BT_GameStartFirst.Location = new Point(226, 613);
			BT_GameStartFirst.Name = "BT_GameStartFirst";
			BT_GameStartFirst.Size = new Size(75, 23);
			BT_GameStartFirst.TabIndex = 1;
			BT_GameStartFirst.Text = "開始(先行)";
			BT_GameStartFirst.UseVisualStyleBackColor = true;
			BT_GameStartFirst.Visible = false;
			BT_GameStartFirst.Click += BT_GameStartFirst_Click;
			// 
			// BT_GameStartSecond
			// 
			BT_GameStartSecond.Location = new Point(322, 613);
			BT_GameStartSecond.Name = "BT_GameStartSecond";
			BT_GameStartSecond.Size = new Size(75, 23);
			BT_GameStartSecond.TabIndex = 2;
			BT_GameStartSecond.Text = "開始(後行)";
			BT_GameStartSecond.UseVisualStyleBackColor = true;
			BT_GameStartSecond.Visible = false;
			BT_GameStartSecond.Click += BT_GameStartSecond_Click;
			// 
			// BT_Pass
			// 
			BT_Pass.Location = new Point(423, 613);
			BT_Pass.Name = "BT_Pass";
			BT_Pass.Size = new Size(75, 23);
			BT_Pass.TabIndex = 3;
			BT_Pass.Text = "パス";
			BT_Pass.UseVisualStyleBackColor = true;
			BT_Pass.Visible = false;
			BT_Pass.Click += BT_Pass_Click;
			// 
			// LB_BlackNum
			// 
			LB_BlackNum.AutoSize = true;
			LB_BlackNum.Location = new Point(12, 25);
			LB_BlackNum.Name = "LB_BlackNum";
			LB_BlackNum.Size = new Size(37, 15);
			LB_BlackNum.TabIndex = 4;
			LB_BlackNum.Text = "●：0";
			// 
			// LB_WhitNum
			// 
			LB_WhiteNum.AutoSize = true;
			LB_WhiteNum.Location = new Point(562, 25);
			LB_WhiteNum.Name = "LB_WhitNum";
			LB_WhiteNum.Size = new Size(37, 15);
			LB_WhiteNum.TabIndex = 6;
			LB_WhiteNum.Text = "〇：0";
			// 
			// Form1
			// 
			AutoScaleDimensions = new SizeF(7F, 15F);
			AutoScaleMode = AutoScaleMode.Font;
			ClientSize = new Size(624, 661);
			Controls.Add(LB_WhiteNum);
			Controls.Add(LB_BlackNum);
			Controls.Add(BT_Pass);
			Controls.Add(BT_GameStartSecond);
			Controls.Add(BT_GameStartFirst);
			Controls.Add(bt_prepare);
			Name = "Form1";
			Text = "Form1";
			ResumeLayout(false);
			PerformLayout();
		}

		#endregion

		private Button bt_prepare;
		private Button BT_GameStartFirst;
		private Button BT_GameStartSecond;
		private Button BT_Pass;
		private Label LB_BlackNum;
		private Label LB_WhiteNum;
	}
}
