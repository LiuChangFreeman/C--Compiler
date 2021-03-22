using FirstFloor.ModernUI.Windows.Controls;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
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
    /// Interaction logic for LR_1_.xaml
    /// </summary>
    public partial class LR1 : ModernWindow
    {
        public LR1()
        {
            InitializeComponent();
            ReadTable();
        }
        StreamReader sr = new StreamReader("../../Source/lr(1).table", Encoding.Default);
        ObservableCollection<LR1TableItem> ItemList = new ObservableCollection<LR1TableItem>();
        private void ReadTable()
        {
            TableView.ItemsSource = ItemList;
            

            sr.ReadLine();
            TableView.Dispatcher.BeginInvoke(DispatcherPriority.Background, new AddItemDelegate(addItem));
        }
        private delegate void AddItemDelegate();
        private void addItem()
        {
            String line;
            if((line = sr.ReadLine()) != null)
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
                LR1TableItem temp = new LR1TableItem(data);
                ItemList.Add(temp);
                TableView.Dispatcher.BeginInvoke(DispatcherPriority.Background, new AddItemDelegate(addItem));
            }
            else
            {
                sr.Close();
                MainWindow temp= (MainWindow)Application.Current.MainWindow;
                temp.Semantic.IsEnabled = true;
            }
        }

        private void Grammer_Click(object sender, RoutedEventArgs e)
        {
            Grammer page = new Grammer();
            page.Show();
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
