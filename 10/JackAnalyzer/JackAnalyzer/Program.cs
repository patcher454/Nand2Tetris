using System.Runtime.InteropServices;

namespace JackAnalyzer;

internal class Program
{
    static void Main(string[] args)
    {
        Analyzer analyzer = new Analyzer();
        analyzer.compilation(args[0]);
    }
}