using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace JackAnalyzer
{
    internal class Analyzer
    {
        const string JACK_EXTENSION = ".jack";

        private List<string> getFileList(string path)
        {
            var list = new List<string>();
            if (path.EndsWith(JACK_EXTENSION))
            {
                list.Add(path);
                return list;
            }

            DirectoryInfo directoryInfo = new DirectoryInfo(path);
            foreach (var item in directoryInfo.GetFiles())
            {
                if (item.Extension.CompareTo(JACK_EXTENSION) == 0)
                {
                    list.Add(Path.Combine(path,item.Name).ToString());
                }
            }
            return list;
        }

        private string getFileName(string path)
        {
            if (path.EndsWith(JACK_EXTENSION))
            {
                return path.Replace(JACK_EXTENSION, "");
            }
            return path;
        }

        public void compilation(string folderPath)
        {
            foreach (var file in getFileList(folderPath))
            {
                CompilationEngine compilationEngine = new CompilationEngine(getFileName(file), file);
                compilationEngine.CompileClass();
            }
        }

    }
}
