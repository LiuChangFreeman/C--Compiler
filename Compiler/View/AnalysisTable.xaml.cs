using Compiler.Model;
using Microsoft.UI;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Text;
using System.Threading.Tasks;
using Windows.Foundation;
using Windows.Foundation.Collections;

// To learn more about WinUI, the WinUI project structure,
// and more about our project templates, see: http://aka.ms/winui-project-info.

namespace Compiler.View
{
    /// <summary>
    /// An empty window that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class AnalysisTable : Window
    {
        public AnalysisTable()
        {
            this.InitializeComponent();
            InitWindow();
            InitTable();
        }

        private void InitWindow()
        {
            IntPtr hWnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
            WindowId windowId = Win32Interop.GetWindowIdFromWindow(hWnd);
            AppWindow appWindow = AppWindow.GetFromWindowId(windowId);
            var size = new Windows.Graphics.SizeInt32();
            size.Width = 1280;
            size.Height = 960;
            appWindow.Resize(size);
            appWindow.SetIcon("icon.ico");
            this.Title = "LR(1)语义分析过程表";
        }

        List<AnalysisTableItem> ItemList = new List<AnalysisTableItem>();

        private async void InitTable()
        {
            await Task.Run(ReadTable);
            DataGrid.ItemsSource = ItemList;
            Progress.Visibility = Visibility.Collapsed;
        }

        private List<AnalysisTableItem> ReadTable()
        {
            string sourceFolder = Storage.getStoragePath("Source");
            string tableFilePath = Path.Combine(sourceFolder, "analysis.table");
            StreamReader sr = new StreamReader(tableFilePath, Encoding.Default);
            sr.ReadLine();
            string line;
            while ((line = sr.ReadLine()) != null)
            {
                var array = line.ToString().Split('\t');
                List<string> data = new List<string>();
                foreach (string item in array)
                {
                    if (item != "\n")
                    {
                        data.Add(item);
                    }
                }
                AnalysisTableItem temp = new AnalysisTableItem(data);
                ItemList.Add(temp);
            }
            sr.Close();
            return ItemList;
        }
    }
}
