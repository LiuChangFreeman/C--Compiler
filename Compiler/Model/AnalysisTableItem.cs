using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Compiler.Model
{
    class AnalysisTableItem:INotifyPropertyChanged
    {
        public AnalysisTableItem(List<string> data)
        {
            step = data[0];
            current = data[1];
            input = data[2];
            script = data[3];
            status = data[4];
            action= data[5];
            gotostatus= data[6];
        }
        public event PropertyChangedEventHandler PropertyChanged;
        private string _step;
        public string step
        {
            get { return _step; }
            set { _step = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("step")); }
        }

        private string _current;
        public string current
        {
            get { return _current; }
            set { _current = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("current")); }
        }

        private string _input;
        public string input
        {
            get { return _input; }
            set { _input = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("input")); }
        }

        private string _script;
        public string script
        {
            get { return _script; }
            set { _script = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("script")); }
        }

        private string _action;
        public string action
        {
            get { return _action; }
            set { _action = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("action")); }
        }

        private string _status;
        public string status
        {
            get { return _status; }
            set { _status = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("status")); }
        }

        private string _gotostatus;
        public string gotostatus
        {
            get { return _gotostatus; }
            set { _gotostatus = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("gotostatus")); }
        }
    }
}
