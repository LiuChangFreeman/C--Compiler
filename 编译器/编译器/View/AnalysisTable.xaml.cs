using FirstFloor.ModernUI.Windows.Controls;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
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
using System.Windows.Threading;
using 编译器.Model;

namespace 编译器.View
{
    /// <summary>
    /// Interaction logic for AnalysisTable.xaml
    /// </summary>
    public partial class AnalysisTable : ModernWindow
    {
        public AnalysisTable()
        {
            InitializeComponent();
            InitializeComponent();
            ReadTable();
        }
        StreamReader sr = new StreamReader("../../Source/analysis.table", Encoding.Default);
        ObservableCollection<AnalysisTableItem> ItemList = new ObservableCollection<AnalysisTableItem>();
        private void ReadTable()
        {
            TableView.ItemsSource = ItemList;
            TableView.Dispatcher.BeginInvoke(DispatcherPriority.Background, new AddItemDelegate(addItem));
        }
        private delegate void AddItemDelegate();
        private void addItem()
        {
            String line;
            if ((line = sr.ReadLine()) != null)
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
                TableView.Dispatcher.BeginInvoke(DispatcherPriority.Background, new AddItemDelegate(addItem));
            }
            else
            {
                sr.Close();
                MainWindow temp = (MainWindow)Application.Current.MainWindow;
                temp.Mips.IsEnabled = true;
            }
        }

        private void scrollViewer_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
        {
            var eventArg = new MouseWheelEventArgs(e.MouseDevice, e.Timestamp, e.Delta);
            eventArg.RoutedEvent = UIElement.MouseWheelEvent;
            eventArg.Source = sender;
            scrollViewer.RaiseEvent(eventArg);
        }
    }
}
