using FirstFloor.ModernUI.Windows.Controls;
using ICSharpCode.AvalonEdit.Highlighting;
using IronPython.Hosting;
using IronPython.Runtime;
using Microsoft.Scripting.Hosting;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using 编译器.Model;
using 编译器.View;

namespace 编译器
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : ModernWindow
    {
        public MainWindow()
        {
            InitializeComponent();
            CodeEditor.Load(@"../../Source/test.c");
            CodeEditor.ShowLineNumbers = true;
            CodeEditor.SyntaxHighlighting= HighlightingManager.Instance.GetDefinitionByExtension(".c");
            Syntactic.IsEnabled = false;
            Semantic.IsEnabled = false;
            Mips.IsEnabled = false;
            BootEngine();
        }

        ScriptEngine engine;

        private void ScrollViewer_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
        {
            var eventArg = new MouseWheelEventArgs(e.MouseDevice, e.Timestamp, e.Delta);
            eventArg.RoutedEvent = UIElement.MouseWheelEvent;
            eventArg.Source = sender;
            scrollViewer.RaiseEvent(eventArg);
        }

        private void CodeEditor_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
        {
            var eventArg = new MouseWheelEventArgs(e.MouseDevice, e.Timestamp, e.Delta);
            eventArg.RoutedEvent = UIElement.MouseWheelEvent;
            eventArg.Source = sender;
            CodeEditorScrollViewer.RaiseEvent(eventArg);
        }

        private dynamic LexcialAnalyzer()
        {
            dynamic py = engine.ExecuteFile(@"../../Source/LexcialAnalyzer.py");
            return py.main(@"../../Source/test.c");
        }

        private dynamic SyntaxParser()
        {
            dynamic result = null;
            try
            {
                dynamic py = engine.ExecuteFile(@"../../Source/MipsGenerate.py");
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
                dynamic py = engine.ExecuteFile(@"../../Source/MipsGenerate.py");
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
                dynamic py = engine.ExecuteFile(@"../../Source/MipsGenerate.py");
                return py.MipsGenerate();
            }
            catch
            {
                result = false;
            }
            return result;
        }

        private async void BootEngine()
        {
            engine=await Task.Run(() => {
                return Python.CreateEngine();
            });
        }

        private async void Lexcial_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            string code = CodeEditor.Text;
            FileStream fs = new FileStream("../../Source/test.c", FileMode.Create);
            byte[] data = System.Text.Encoding.Default.GetBytes(code);
            fs.Write(data, 0, data.Length);
            fs.Flush();
            fs.Close();
            var result=await Task.Run(() =>{
                    return LexcialAnalyzer();
                }
            );
            Progress.Visibility = Visibility.Collapsed;
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
            TokenView.ItemsSource = tokens;
            TokenView.Visibility = Visibility.Visible;
            CodeEditor.Load(@"../../Source/test.c");
            Syntactic.IsEnabled = true;
        }

        private async void Syntactic_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            var result = await Task.Run(() =>{
                return SyntaxParser();
            });
            Progress.Visibility = Visibility.Collapsed;
            if (result==true)
            {
                ModernDialog modernDialog = new ModernDialog
                {
                    Title = "LR(1)分析表建立成功!",
                    Content ="查看结果？"
                };
                modernDialog.Buttons = new Button[] { modernDialog.OkButton, modernDialog.CancelButton };
                modernDialog.ShowDialog();
                result=modernDialog.MessageBoxResult.ToString();
                if (result=="OK")
                {
                    LR1 page = new LR1();
                    page.Show();
                }
                else
                {
                    Semantic.IsEnabled = true;
                }
            }
        }

        private async void Semantic_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            var result = await Task.Run(() => {
                return SemanticAnalysis();
            });
            Progress.Visibility = Visibility.Collapsed;
            if (result == true)
            {
                ModernDialog modernDialog = new ModernDialog
                {
                    Title = "生成中间代码成功!",
                    Content = "查看结果？"
                };
                modernDialog.Buttons = new Button[] { modernDialog.OkButton, modernDialog.CancelButton };
                modernDialog.ShowDialog();
                result = modernDialog.MessageBoxResult.ToString();
                if (result == "OK")
                {
                    AnalysisTable page = new AnalysisTable();
                    page.Show();
                    MiddleCode page2 = new MiddleCode();
                    page2.Show();
                }
                else
                {
                    Mips.IsEnabled = true;
                }
                
            }
            else
            {
                ModernDialog modernDialog = new ModernDialog
                {
                    Title = "语义分析失败!",
                    Content = "请检查代码合法性!"
                };
                modernDialog.ShowDialog();
            }
        }

        private async void Mips_Click(object sender, RoutedEventArgs e)
        {
            Progress.Visibility = Visibility.Visible;
            var result = await Task.Run(() => {
                return MipsGenerate();
            });
            Progress.Visibility = Visibility.Collapsed;
            if (result == true)
            {
                ModernDialog modernDialog = new ModernDialog
                {
                    Title = "Mips生成汇编成功!",
                    Content = "查看结果？"
                };
                modernDialog.Buttons = new Button[] { modernDialog.OkButton, modernDialog.CancelButton };
                modernDialog.ShowDialog();
                result = modernDialog.MessageBoxResult.ToString();
                if (result == "OK")
                {
                    Mips page = new Mips();
                    page.Show();
                }
            }
        }
    }
}
