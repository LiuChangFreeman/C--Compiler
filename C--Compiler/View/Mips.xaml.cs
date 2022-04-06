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
using Microsoft.Web.WebView2.Core;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices.WindowsRuntime;
using Windows.ApplicationModel;
using Windows.Foundation;
using Windows.Foundation.Collections;

// To learn more about WinUI, the WinUI project structure,
// and more about our project templates, see: http://aka.ms/winui-project-info.

namespace Compiler.View
{
    /// <summary>
    /// An empty window that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class Mips : Window
    {
        public Mips()
        {
            this.InitializeComponent();
            InitWindow();
        }

        private void InitWindow()
        {
            IntPtr hWnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
            WindowId windowId = Win32Interop.GetWindowIdFromWindow(hWnd);
            AppWindow appWindow = AppWindow.GetFromWindowId(windowId);
            var size = new Windows.Graphics.SizeInt32();
            size.Width = 710;
            size.Height = 850;
            appWindow.Resize(size);
            appWindow.SetIcon("icon.ico");
            this.Title = "Mips汇编代码";
            this.Closed += (o, e) =>
            {
                MainWebView.Close();
            };
            LoadedWebview();
        }

        private async void LoadedWebview()
        {
            var sourceFolder = Storage.getStoragePath("Source");
            await MainWebView.EnsureCoreWebView2Async();
            var coreWebView = MainWebView.CoreWebView2;
            coreWebView.Settings.IsZoomControlEnabled = false;
            coreWebView.Settings.AreDevToolsEnabled = true;
            coreWebView.Navigate(Storage.getEditorPath());
            coreWebView.WebMessageReceived += async (s, e) =>
            {
                message msg = JsonConvert.DeserializeObject<message>(e.TryGetWebMessageAsString());
                if (msg.type == "init_code")
                {
                    string asmFilePath = Path.Combine(sourceFolder, "result.asm");
                    string asmFileSource = await File.ReadAllTextAsync(asmFilePath);
                    msg.value = asmFileSource;
                    coreWebView.PostWebMessageAsString(JsonConvert.SerializeObject(msg));
                }
            };
        }
    }
}
