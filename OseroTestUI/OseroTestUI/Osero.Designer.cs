namespace OseroTestUI
{
	partial class Osero
	{
		/// <summary> 
		/// 必要なデザイナー変数です。
		/// </summary>
		private System.ComponentModel.IContainer components = null;

		/// <summary> 
		/// 使用中のリソースをすべてクリーンアップします。
		/// </summary>
		/// <param name="disposing">マネージド リソースを破棄する場合は true を指定し、その他の場合は false を指定します。</param>
		protected override void Dispose(bool disposing)
		{
			if (disposing && (components != null)) {
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		#region コンポーネント デザイナーで生成されたコード

		/// <summary> 
		/// デザイナー サポートに必要なメソッドです。このメソッドの内容を 
		/// コード エディターで変更しないでください。
		/// </summary>
		private void InitializeComponent()
		{
			label = new Label();
			SuspendLayout();
			// 
			// label
			// 
			label.AutoSize = true;
			label.Font = new Font("Yu Gothic UI", 30F);
			label.Location = new Point(1, 5);
			label.Name = "label";
			label.Size = new Size(0, 54);
			label.TabIndex = 0;
			// 
			// Osero
			// 
			AutoScaleDimensions = new SizeF(7F, 15F);
			AutoScaleMode = AutoScaleMode.Font;
			BackColor = Color.White;
			Controls.Add(label);
			Name = "Osero";
			Size = new Size(64, 64);
			Click += Osero_Click;
			ResumeLayout(false);
			PerformLayout();
		}

		#endregion

		private Label label;
	}
}
