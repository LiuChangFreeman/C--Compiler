using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using Microsoft.UI.Xaml.Data;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Navigation;
using Windows.ApplicationModel;
using Compiler.Model;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.IO;
using System.Text;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using Windows.Foundation;
using Windows.Foundation.Collections;
using IronPython.Hosting;
using IronPython.Runtime;
using Microsoft.Scripting.Hosting;
using Microsoft.Web.WebView2.Core;
using Newtonsoft.Json;
using Microsoft.UI;
using Microsoft.UI.Windowing;
using Compiler.View;

// To learn more about WinUI, the WinUI project structure,
// and more about our project templates, see: http://aka.ms/winui-project-info.

namespace Compiler
{
    /// <summary>
    /// An empty window that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();
            IntPtr hWnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
            WindowId windowId = Win32Interop.GetWindowIdFromWindow(hWnd);
            AppWindow appWindow = AppWindow.GetFromWindowId(windowId);
            var size = new Windows.Graphics.SizeInt32();
            size.Width = 1280;
            size.Height = 960;
            appWindow.Resize(size);
            appWindow.SetIcon("icon.ico");

            this.Title = "C--编译器";
            Lexcial.IsEnabled = false;
            Syntactic.IsEnabled = false;
            Semantic.IsEnabled = false;
            Mips.IsEnabled = false;
            LoadedWebview();
            this.Closed += (o, e) =>
            {
                MainWebView.Close();
            };
        }

        ScriptEngine engine;
        string sourceFolder;
        CoreWebView2 coreWebView;

        private async void LoadedWebview()
        {
            await Storage.ensureAsserts();
            sourceFolder = Storage.getStoragePath("Source");
            engine = await Task.Run(() => {
                return Python.CreateEngine();
            });
            ICollection<string> Paths = engine.GetSearchPaths();
            Paths.Add(sourceFolder);
            Paths.Add(getSourcePath("Lib"));
            engine.SetSearchPaths(Paths);

            await MainWebView.EnsureCoreWebView2Async();
            coreWebView = MainWebView.CoreWebView2;
            coreWebView.Settings.IsZoomControlEnabled=false;
            coreWebView.Settings.AreDevToolsEnabled = true;
            coreWebView.Navigate(Storage.getEditorPath());
            coreWebView.WebMessageReceived += async(s, e) =>
            {
                message msg = JsonConvert.DeserializeObject<message>(e.TryGetWebMessageAsString());
                if (msg.type== "init_code")
                {
                    string pyFileSource = await File.ReadAllTextAsync(getSourcePath("test.c"));
                    msg.value = pyFileSource;
                    coreWebView.PostWebMessageAsString(JsonConvert.SerializeObject(msg));
                    Lexcial.IsEnabled = true;
                }
                else if (msg.type == "return_code")
                {
                    FileStream fs = new FileStream(getSourcePath("test.c--"), FileMode.Create);
                    byte[] data = Encoding.Default.GetBytes(msg.value);
                    fs.Write(data, 0, data.Length);
                    fs.Close();
                    var result = await Task.Run(() =>
                    {
                        return LexcialAnalyzer();
                    });
                    List<token> tokens = new List<token>();
                    foreach (var item in result)
                    {
                        var temp = item as PythonDictionary;
                        token Token = new token();
                        Token.type = temp["type"].ToString();
                        Token.value = temp["name"].ToString();
                        Token.row = temp["row"].ToString();
                        Token.colum = temp["colum"].ToString();
                        tokens.Add(Token);
                    }
                    DataGrid.ItemsSource = tokens;
                    DataGrid.Visibility = Visibility.Visible;
                    Progress.Visibility = Visibility.Collapsed;
                    Syntactic.IsEnabled = true;
                }
            };
        }

        private string getSourcePath(string path)
        {
            return Path.Combine(sourceFolder, path);
        }

        private dynamic LexcialAnalyzer()
        {
            dynamic py = engine.ExecuteFile(getSourcePath("LexcialAnalyzer.py"));
            return py.main(getSourcePath("test.c--"));
        }

        private dynamic SyntaxParser()
        {
            dynamic result = null;
            try
            {
                dynamic py = engine.ExecuteFile(getSourcePath("MipsGenerate.py"));
                result = py.SyntaxParserTable();
            }
            catch
            {
                result = false;
            }
            return result;
        }

        private dynamic SemanticAnalysis()
        {
            dynamic result = null;
            try
            {
                dynamic py = engine.ExecuteFile(getSourcePath("MipsGenerate.py"));
                return py.BeginSemanticAnalysis();
            }
            catch
            {
                result = false;
            }
            return result;
        }

        private dynamic MipsGenerate()
        {
            dynamic result = null;
            try
            {
                dynamic py = engine.ExecuteFile(getSourcePath("MipsGenerate.py"));
                return py.MipsGenerate();
            }
            catch
            {
                result = false;
            }
            return result;
        }

        private void Lexcial_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            message msg = new message{ type = "get_code" };
            coreWebView.PostWebMessageAsString(JsonConvert.SerializeObject(msg));
        }

        private async void Syntactic_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            var result = await Task.Run(() => {
                return SyntaxParser();
            });
            Progress.Visibility = Visibility.Collapsed;
            if(result)
            {
                Semantic.IsEnabled = true;
                ContentDialog dialog = new ContentDialog();
                dialog.XamlRoot = this.Content.XamlRoot;
                dialog.Title = "LR(1)分析表建立成功";
                dialog.PrimaryButtonText = "是";
                dialog.SecondaryButtonText = "否";
                dialog.DefaultButton = ContentDialogButton.Primary;
                dialog.Content = new ContentDialogContent();
                var choice = await dialog.ShowAsync();
                if (choice == ContentDialogResult.Primary)
                {
                    LR_1 page = new LR_1();
                    page.Activate();
                }
            }
            else
            {
                ContentDialog dialog = new ContentDialog();
                dialog.XamlRoot = this.Content.XamlRoot;
                dialog.Title = "LR(1)分析表建立失败";
                dialog.PrimaryButtonText = "确定";
                await dialog.ShowAsync();
            }
        }

        private async void Semantic_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            var result = await Task.Run(() => {
                return SemanticAnalysis();
            });
            Progress.Visibility = Visibility.Collapsed;
            if (result)
            {
                Mips.IsEnabled = true;
                ContentDialog dialog = new ContentDialog();
                dialog.XamlRoot = this.Content.XamlRoot;
                dialog.Title = "生成中间代码成功";
                dialog.PrimaryButtonText = "是";
                dialog.SecondaryButtonText = "否";
                dialog.DefaultButton = ContentDialogButton.Primary;
                dialog.Content = new ContentDialogContent();
                var choice = await dialog.ShowAsync();
                if (choice == ContentDialogResult.Primary)
                {
                    MiddleCode page_1 = new MiddleCode();
                    page_1.Activate();
                    AnalysisTable page_2 = new AnalysisTable();
                    page_2.Activate();
                }
            }
            else
            {
                ContentDialog dialog = new ContentDialog();
                dialog.XamlRoot = this.Content.XamlRoot;
                dialog.Title = "语义分析子程序执行失败";
                dialog.PrimaryButtonText = "确定";
                await dialog.ShowAsync();
            }
        }

        private async void Mips_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            var result = await Task.Run(() => {
                return MipsGenerate();
            });
            Progress.Visibility = Visibility.Collapsed;
            if (result)
            {
                ContentDialog dialog = new ContentDialog();
                dialog.XamlRoot = this.Content.XamlRoot;
                dialog.Title = "生成Mips汇编成功";
                dialog.PrimaryButtonText = "是";
                dialog.SecondaryButtonText = "否";
                dialog.DefaultButton = ContentDialogButton.Primary;
                dialog.Content = new ContentDialogContent();
                var choice = await dialog.ShowAsync();
                if (choice == ContentDialogResult.Primary)
                {
                    Mips page = new Mips();
                    page.Activate();
                }
            }
            else
            {
                ContentDialog dialog = new ContentDialog();
                dialog.XamlRoot = this.Content.XamlRoot;
                dialog.Title = "生成Mips汇编失败";
                dialog.PrimaryButtonText = "确定";
                await dialog.ShowAsync();
            }
        }

        private void Grammer_Click(object sender, RoutedEventArgs e)
        {
            Grammer page = new Grammer();
            page.Activate();
        }
    }
}
