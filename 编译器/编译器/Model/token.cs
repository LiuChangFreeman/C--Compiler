using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;

namespace 编译器.Model
{
    class token : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;
        private string _type;
        public string type
        {
            get { return _type; }
            set { _type = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("type")); }
        }
        private string _value;
        public string value
        {
            get { return _value; }
            set { _value = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("value")); }
        }
        private string _row;
        public string row
        {
            get { return _row; }
            set { _row = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("row")); }
        }
        private string _colum;
        public string colum
        {
            get { return _colum; }
            set { _colum = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("colum")); }
        }

    }
}
