using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace 编译器.Model
{
    class LR1TableItem : INotifyPropertyChanged
    {
        public LR1TableItem(List<string> data)
        {
            item0 = data[0];
            item1 = data[1];
            item2 = data[2];
            item3 = data[3];
            item4 = data[4];
            item5 = data[5];
            item6 = data[6];
            item7 = data[7];
            item8 = data[8];
            item9 = data[9];
            item10 = data[10];
            item11 = data[11];
            item12 = data[12];
            item13 = data[13];
            item14 = data[14];
            item15 = data[15];
            item16 = data[16];
            item17 = data[17];
            item18 = data[18];
            item19 = data[19];
            item20 = data[20];
            item21 = data[21];
            item22 = data[22];
            item23 = data[23];
            item24 = data[24];
            item25 = data[25];
            item26 = data[26];
            item27 = data[27];
            item28 = data[28];
            item29 = data[29];
            item30 = data[30];
            item31 = data[31];
            item32 = data[32];
            item33 = data[33];
            item34 = data[34];
            item35 = data[35];
            item36 = data[36];
            item37 = data[37];
            item38 = data[38];
            item39 = data[39];
            item40 = data[40];
            item41 = data[41];
            item42 = data[42];
            item43 = data[43];
            item44 = data[44];
            item45 = data[45];
            item46 = data[46];
            item47 = data[47];
            item48 = data[48];
            item49 = data[49];
            item50 = data[50];
            item51 = data[51];
            item52 = data[52];
            item53 = data[53];
            item54 = data[54];
            item55 = data[55];
            item56 = data[56];
            item57 = data[57];
            item58 = data[58];
            item59 = data[59];
            item60 = data[60];
            item61 = data[61];
            item62 = data[62];
            item63 = data[63];
            item64 = data[64];
        }
        public event PropertyChangedEventHandler PropertyChanged;
        private string _item;
        public string item
        {
            get { return _item; }
            set { _item = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item")); }
        }
        private string _item0;
        public string item0
        {
            get { return _item0; }
            set { _item0 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item0")); }
        }

        private string _item1;
        public string item1
        {
            get { return _item1; }
            set { _item1 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item1")); }
        }

        private string _item2;
        public string item2
        {
            get { return _item2; }
            set { _item2 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item2")); }
        }

        private string _item3;
        public string item3
        {
            get { return _item3; }
            set { _item3 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item3")); }
        }

        private string _item4;
        public string item4
        {
            get { return _item4; }
            set { _item4 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item4")); }
        }

        private string _item5;
        public string item5
        {
            get { return _item5; }
            set { _item5 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item5")); }
        }

        private string _item6;
        public string item6
        {
            get { return _item6; }
            set { _item6 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item6")); }
        }

        private string _item7;
        public string item7
        {
            get { return _item7; }
            set { _item7 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item7")); }
        }

        private string _item8;
        public string item8
        {
            get { return _item8; }
            set { _item8 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item8")); }
        }

        private string _item9;
        public string item9
        {
            get { return _item9; }
            set { _item9 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item9")); }
        }

        private string _item10;
        public string item10
        {
            get { return _item10; }
            set { _item10 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item10")); }
        }

        private string _item11;
        public string item11
        {
            get { return _item11; }
            set { _item11 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item11")); }
        }

        private string _item12;
        public string item12
        {
            get { return _item12; }
            set { _item12 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item12")); }
        }

        private string _item13;
        public string item13
        {
            get { return _item13; }
            set { _item13 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item13")); }
        }

        private string _item14;
        public string item14
        {
            get { return _item14; }
            set { _item14 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item14")); }
        }

        private string _item15;
        public string item15
        {
            get { return _item15; }
            set { _item15 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item15")); }
        }

        private string _item16;
        public string item16
        {
            get { return _item16; }
            set { _item16 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item16")); }
        }

        private string _item17;
        public string item17
        {
            get { return _item17; }
            set { _item17 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item17")); }
        }

        private string _item18;
        public string item18
        {
            get { return _item18; }
            set { _item18 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item18")); }
        }

        private string _item19;
        public string item19
        {
            get { return _item19; }
            set { _item19 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item19")); }
        }

        private string _item20;
        public string item20
        {
            get { return _item20; }
            set { _item20 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item20")); }
        }

        private string _item21;
        public string item21
        {
            get { return _item21; }
            set { _item21 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item21")); }
        }

        private string _item22;
        public string item22
        {
            get { return _item22; }
            set { _item22 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item22")); }
        }

        private string _item23;
        public string item23
        {
            get { return _item23; }
            set { _item23 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item23")); }
        }

        private string _item24;
        public string item24
        {
            get { return _item24; }
            set { _item24 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item24")); }
        }

        private string _item25;
        public string item25
        {
            get { return _item25; }
            set { _item25 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item25")); }
        }

        private string _item26;
        public string item26
        {
            get { return _item26; }
            set { _item26 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item26")); }
        }

        private string _item27;
        public string item27
        {
            get { return _item27; }
            set { _item27 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item27")); }
        }

        private string _item28;
        public string item28
        {
            get { return _item28; }
            set { _item28 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item28")); }
        }

        private string _item29;
        public string item29
        {
            get { return _item29; }
            set { _item29 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item29")); }
        }

        private string _item30;
        public string item30
        {
            get { return _item30; }
            set { _item30 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item30")); }
        }

        private string _item31;
        public string item31
        {
            get { return _item31; }
            set { _item31 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item31")); }
        }

        private string _item32;
        public string item32
        {
            get { return _item32; }
            set { _item32 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item32")); }
        }

        private string _item33;
        public string item33
        {
            get { return _item33; }
            set { _item33 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item33")); }
        }

        private string _item34;
        public string item34
        {
            get { return _item34; }
            set { _item34 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item34")); }
        }

        private string _item35;
        public string item35
        {
            get { return _item35; }
            set { _item35 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item35")); }
        }

        private string _item36;
        public string item36
        {
            get { return _item36; }
            set { _item36 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item36")); }
        }

        private string _item37;
        public string item37
        {
            get { return _item37; }
            set { _item37 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item37")); }
        }

        private string _item38;
        public string item38
        {
            get { return _item38; }
            set { _item38 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item38")); }
        }

        private string _item39;
        public string item39
        {
            get { return _item39; }
            set { _item39 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item39")); }
        }

        private string _item40;
        public string item40
        {
            get { return _item40; }
            set { _item40 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item40")); }
        }

        private string _item41;
        public string item41
        {
            get { return _item41; }
            set { _item41 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item41")); }
        }

        private string _item42;
        public string item42
        {
            get { return _item42; }
            set { _item42 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item42")); }
        }

        private string _item43;
        public string item43
        {
            get { return _item43; }
            set { _item43 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item43")); }
        }

        private string _item44;
        public string item44
        {
            get { return _item44; }
            set { _item44 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item44")); }
        }

        private string _item45;
        public string item45
        {
            get { return _item45; }
            set { _item45 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item45")); }
        }

        private string _item46;
        public string item46
        {
            get { return _item46; }
            set { _item46 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item46")); }
        }

        private string _item47;
        public string item47
        {
            get { return _item47; }
            set { _item47 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item47")); }
        }

        private string _item48;
        public string item48
        {
            get { return _item48; }
            set { _item48 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item48")); }
        }

        private string _item49;
        public string item49
        {
            get { return _item49; }
            set { _item49 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item49")); }
        }

        private string _item50;
        public string item50
        {
            get { return _item50; }
            set { _item50 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item50")); }
        }

        private string _item51;
        public string item51
        {
            get { return _item51; }
            set { _item51 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item51")); }
        }

        private string _item52;
        public string item52
        {
            get { return _item52; }
            set { _item52 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item52")); }
        }

        private string _item53;
        public string item53
        {
            get { return _item53; }
            set { _item53 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item53")); }
        }

        private string _item54;
        public string item54
        {
            get { return _item54; }
            set { _item54 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item54")); }
        }

        private string _item55;
        public string item55
        {
            get { return _item55; }
            set { _item55 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item55")); }
        }

        private string _item56;
        public string item56
        {
            get { return _item56; }
            set { _item56 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item56")); }
        }

        private string _item57;
        public string item57
        {
            get { return _item57; }
            set { _item57 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item57")); }
        }

        private string _item58;
        public string item58
        {
            get { return _item58; }
            set { _item58 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item58")); }
        }

        private string _item59;
        public string item59
        {
            get { return _item59; }
            set { _item59 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item59")); }
        }

        private string _item60;
        public string item60
        {
            get { return _item60; }
            set { _item60 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item60")); }
        }

        private string _item61;
        public string item61
        {
            get { return _item61; }
            set { _item61 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item61")); }
        }

        private string _item62;
        public string item62
        {
            get { return _item62; }
            set { _item62 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item62")); }
        }

        private string _item63;
        public string item63
        {
            get { return _item63; }
            set { _item63 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item63")); }
        }
        private string _item64;
        public string item64
        {
            get { return _item64; }
            set { _item64 = value; PropertyChanged?.Invoke(this, new PropertyChangedEventArgs("item64")); }
        }
    }
}
