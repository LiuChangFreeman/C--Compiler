using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Compiler.Model
{
    class message
    {
        private string _type;
        public string type
        {
            get { return _type; }
            set { _type = value;}
        }
        private string _value;
        public string value
        {
            get { return _value; }
            set { _value = value;}
        }
    }
}
