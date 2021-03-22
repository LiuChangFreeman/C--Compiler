using FirstFloor.ModernUI.Windows.Controls;
using ICSharpCode.AvalonEdit.Highlighting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace 编译器.View
{
    /// <summary>
    /// Interaction logic for Mips.xaml
    /// </summary>
    public partial class Mips : ModernWindow
    {
        public Mips()
        {
            InitializeComponent();
            InitializeComponent();
            CodeEditor.Load(@"../../Source/result.asm");
            CodeEditor.ShowLineNumbers = true;
            CodeEditor.SyntaxHighlighting = HighlightingManager.Instance.GetDefinitionByExtension(".asm");
        }

        private void CodeEditor_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
        {
            var eventArg = new MouseWheelEventArgs(e.MouseDevice, e.Timestamp, e.Delta);
            eventArg.RoutedEvent = UIElement.MouseWheelEvent;
            eventArg.Source = sender;
            CodeEditor.RaiseEvent(eventArg);
        }
    }
}
