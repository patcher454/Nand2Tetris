using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace JackAnalyzer
{
    internal class Tokenizer
    {

        private List<List<string>> tokens;

        private readonly string[] KEYWORDS = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"];
        private readonly string[] SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"];


        public enum TOKEN_TYPES
        {
            KEYWORD,
            SYMBOL,
            INT_CONST,
            STRING_CONST,
            IDENTIFIER,
        }

        public readonly Dictionary<TOKEN_TYPES, string> TOKEN_TYPE_CODE = new Dictionary<TOKEN_TYPES, string>
        {
            { TOKEN_TYPES.KEYWORD , "keyword" },
            { TOKEN_TYPES.SYMBOL, "symbol" },
            { TOKEN_TYPES.INT_CONST, "int_const" },
            { TOKEN_TYPES.STRING_CONST, "string_const" },
            { TOKEN_TYPES.IDENTIFIER, "identifier" }
        };

        private int counter = -1;



        private bool CheckStringConstant(char value)
        {
            return value == '"';
        }

        private bool CheckIntegerConstant(char value)
        {
            char[] intStringArr = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
            return intStringArr.Contains(value);
        }

        private bool CheckSymbol(char value)
        {
            return SYMBOLS.Contains(value.ToString());
        }

        private List<string> CheckKeep(string value)
        {
            if (KEYWORDS.Contains(value))
            {
                return new List<string> { TOKEN_TYPE_CODE[TOKEN_TYPES.KEYWORD], value };
            }

            if (int.TryParse(value, out int intValue))
            {
                return new List<string> { TOKEN_TYPE_CODE[TOKEN_TYPES.INT_CONST], value };
            }

            return new List<string> { TOKEN_TYPE_CODE[TOKEN_TYPES.IDENTIFIER], value };
        }

        public Tokenizer(string fileName)
        {
            List<string> lines = new List<string>();
            tokens = new List<List<string>>();

            using (StreamReader reader = new StreamReader(fileName))
            {
                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    if (line != null)
                    {
                        var comment = line.IndexOf("//");
                        if (comment >= 0) { line = line[..comment]; }

                        comment = line.IndexOf("/**");
                        if (comment >= 0) { line = line[..comment]; }

                        comment = line.IndexOf("/*");
                        if (comment >= 0) { line = line[..comment]; }

                        line = line.Trim([' ', '\n']);

                        if (line.StartsWith("*")) { continue; }

                        if (line.Length != 0)
                        {
                            lines.Add(line.Trim());
                        }

                    }
                }
            }

            foreach (var line in lines)
            {
                var keep = "";
                for (int i = 0; i < line.Length; i++)
                {
                    if (CheckStringConstant(line[i]) || CheckSymbol(line[i]) || line[i] == ' ')
                    {
                        if (keep.Trim([' ', '\n']).Length != 0)
                        {
                            tokens.Add(CheckKeep(keep));
                            keep = "";
                        }

                        if (CheckStringConstant(line[i]))
                        {
                            var start = i + 1;
                            var end = start + line[start..].IndexOf('"');
                            var content = line[start..end];
                            i = end;
                            tokens.Add(new List<string> { TOKEN_TYPE_CODE[TOKEN_TYPES.STRING_CONST], content });
                            continue;
                        }

                        if (CheckSymbol(line[i]))
                        {
                            tokens.Add(new List<string> { TOKEN_TYPE_CODE[TOKEN_TYPES.SYMBOL], line[i].ToString() });
                        }

                        continue;
                    }

                    keep += line[i];
                }
            }
        }

        public bool HasMoreTokens()
        {
            return tokens.Count > counter + 1;
        }

        public bool Advance()
        {
            if (HasMoreTokens())
            {
                counter++;
                return true;
            }
            return false;
        }

        public bool Back()
        {
            if (counter > 0) {
                counter--;
                return true;
            }
            return false;
        }

        public string GetTokenType()
        {
            return tokens[counter][0];
        }

        public string GetKeyword()
        {
            return tokens[counter][1];
        }

        public string GetSymbol()
        {
            return tokens[counter][1];
        }

        public string GetIdentifier()
        {
            return tokens[counter][0];
        }

        public string GetIntVal()
        {
            return tokens[counter][0];
        }

        public string GetStringVal()
        {
            return tokens[counter][0];
        }
    }
}
