using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Windows;
using Windows.Storage;
using Windows.ApplicationModel;

namespace Compiler.Model
{
    class Storage
    {
        private static string storagePath = ApplicationData.Current.LocalCacheFolder.Path;

        public static string getStoragePath(string path)
        {
            return Path.Combine(storagePath, path);
        }

        public static async Task ensureAsserts()
        {
            string descFolder = getStoragePath("Source");
            if (!Directory.Exists(descFolder))
            {
                string sourceFolder = (await Package.Current.InstalledLocation.GetFolderAsync("Source")).Path;
                CopyFolder(sourceFolder, descFolder);
            }
        }

        private static void CopyFolder(string sourceFolder, string destFolder)
        {
            try
            {
                if (!Directory.Exists(destFolder))
                {
                    Directory.CreateDirectory(destFolder);
                }
                string[] files = Directory.GetFiles(sourceFolder);
                foreach (string file in files)
                {
                    string name = Path.GetFileName(file);
                    string dest = Path.Combine(destFolder, name);
                    File.Copy(file, dest);
                }
                string[] folders = Directory.GetDirectories(sourceFolder);
                foreach (string folder in folders)
                {
                    string dirName = folder.Split('\\')[folder.Split('\\').Length - 1];
                    string destfolder = Path.Combine(destFolder, dirName);
                    CopyFolder(folder, destfolder);
                }
            }
            catch (Exception ex)
            {
                throw new Exception($"copy file Error:{ex.Message}\r\n source:{ex.StackTrace}");
            }
        }
    }
}
