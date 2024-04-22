using JackAnalyzer;

using System;
using System.IO;

public class Writer
{
    private bool isPrint;
    private StreamWriter file;

    public Writer(string fileName, bool isPrint = false)
    {
        this.isPrint = isPrint;
        if (!isPrint)
        {
            this.file = new StreamWriter(fileName + ".xml");
        }
    }

    public void Write(string s)
    {
        if (isPrint)
        {
            Console.WriteLine(s);
        }
        else
        {
            this.file.WriteLine(s);
        }
    }

    public void WriteTag(string type, string s)
    {
        Write($"<{type}> {s} </{type}>");
    }

    public void Close()
    {
        if (!isPrint)
        {
            this.file.Close();
        }
    }
}

public class CompilationEngine
{
    private static readonly string[] OP = { "+", "-", "*", "/", "&", "|", "<", ">", "=" };

    private Writer writer;
    private readonly Tokenizer tokenizer;

    public CompilationEngine(string filename, string filePath)
    {
        this.writer = new Writer(filename);
        this.tokenizer = new Tokenizer(filePath);
    }

    private string GetValue()
    {
        string v = this.tokenizer.GetKeyword();
        string tokenType = this.tokenizer.GetTokenType();
        if (tokenType == tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.SYMBOL]) v = this.tokenizer.GetSymbol();
        if (tokenType ==  tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.IDENTIFIER]) v = this.tokenizer.GetIdentifier();
        if (tokenType == tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.INT_CONST]) v = this.tokenizer.GetIntVal();
        if (tokenType == tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.STRING_CONST]) v = this.tokenizer.GetStringVal();
        return v;
    }

    private bool Require(string type, string? requiredValue = null)
    {
        string v = this.GetValue();
        var flag = tokenizer.GetTokenType() == type;
        if(requiredValue != null)
        {
            flag = flag && v == requiredValue;
        }
        return flag;
    }

    private bool Require(string type, List<string> requiredValues) {
        string v = this.GetValue();
        var flag = tokenizer.GetTokenType() == type;
        if (requiredValues != null)
        {
            flag = flag && requiredValues.Contains(v);
        }
        return flag;
    }

    private bool IsKeyword(string? requiredValue = null) => Require(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.KEYWORD], requiredValue);
    private bool IsSymbol(string? requiredValue = null) => Require(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.SYMBOL], requiredValue);
    private bool IsIdentifier(string? requiredValue = null) => Require(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.IDENTIFIER], requiredValue);
    private bool IsInt(string? requiredValue = null) => Require(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.INT_CONST], requiredValue);
    private bool IsString(string? requiredValue = null) => Require(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.STRING_CONST], requiredValue);
    private bool IsOp() => IsSymbol() && Array.Exists(OP, element => element == this.tokenizer.GetSymbol());

    private bool IsKeyword(List<string> requiredValue) => Require(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.KEYWORD], requiredValue);

    private bool IsSymbol(List<string> requiredValue) => Require(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.SYMBOL], requiredValue);


    private void WriteCurrentTagAndNext()
    {
        string v = this.GetValue();
        if (v == "<") v = "&lt;";
        if (v == ">") v = "&gt;";
        if (v == "\"") v = "&quot;";
        if (v == "&") v = "&amp;";

        string tokenType = this.tokenizer.GetTokenType();
        if (tokenType == tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.STRING_CONST]) tokenType = "stringConstant";
        if (tokenType == tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.INT_CONST]) tokenType = "integerConstant";
        this.writer.WriteTag(tokenType, v);
        this.tokenizer.Advance();
    }

    private void WriteKeyword(string? requiredValue = null) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.KEYWORD], requiredValue);
    private void WriteSymbol(string? requiredValue = null) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.SYMBOL], requiredValue);
    private void WriteIdentifier(string? requiredValue = null) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.IDENTIFIER], requiredValue);
    private void WriteInt(string? requiredValue = null) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.INT_CONST], requiredValue);
    private void WriteString(string? requiredValue = null) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.STRING_CONST], requiredValue);

    private void WriteKeyword(List<string> requiredValue) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.KEYWORD], requiredValue);
    private void WriteSymbol(List<string> requiredValue) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.SYMBOL], requiredValue);
    private void WriteString(List<string> requiredValue) => __Write(tokenizer.TOKEN_TYPE_CODE[Tokenizer.TOKEN_TYPES.STRING_CONST], requiredValue);


    private void __Write(string type, string? requiredValue = null)
    {
        if (Require(type, requiredValue))
        {
            WriteCurrentTagAndNext();
        }
        else
        {
            string v = this.GetValue();
            throw new Exception($"required {type}:{requiredValue} but {v}");
        }
    }

    private void __Write(string type, List<string>? requiredValue = null)
    {
        if (Require(type, requiredValue))
        {
            WriteCurrentTagAndNext();
        }
        else
        {
            string v = this.GetValue();
            throw new Exception($"required {type}:{requiredValue} but {v}");
        }
    }

    public void CompileType()
    {
        WriteCurrentTagAndNext();
    }

    public void CompileClass()
    {
        writer.Write("<class>");
        tokenizer.Advance();
        WriteKeyword("class");
        WriteIdentifier();  // class name
        WriteSymbol("{");

        CompileClassVarDec();
        CompileSubroutine();

        WriteSymbol("}");

        writer.Write("</class>");
        writer.Close();
    }

    public void CompileClassVarDec()
    {
        if (!IsClassVarDec())
        {
            return;
        }

        while (IsClassVarDec())
        {
            writer.Write("<classVarDec>");

            WriteKeyword(new List<string> { "static", "field" });
            CompileType();
            WriteIdentifier();
            while (IsSymbol(","))
            {
                WriteSymbol(",");
                WriteIdentifier();
            }
            WriteSymbol(";");
            writer.Write("</classVarDec>");
        }
    }

    private bool IsClassVarDec() => IsKeyword(new List<string> { "static", "field" });

    public void CompileSubroutine()
    {
        if (!IsSubroutine())
        {
            return;
        }

        while (IsSubroutine())
        {
            writer.Write("<subroutineDec>");
            WriteKeyword(new List<string> { "constructor", "function", "method" });
            CompileType();  // type
            WriteIdentifier();  // Functionname
            WriteSymbol("(");
            writer.Write("<parameterList>");
            CompileParameterList();
            writer.Write("</parameterList>");
            WriteSymbol(")");
            CompileSubroutineBody();
            writer.Write("</subroutineDec>");
        }
    }

    private bool IsSubroutine() => IsKeyword(new List<string> { "constructor", "function", "method" });

    public void CompileParameterList()
    {
        if (!IsParameter())
        {
            return;
        }

        while (IsParameter())
        {
            CompileType();  // type
            WriteIdentifier();  // variable name
            if (IsSymbol(","))
            {
                WriteSymbol(",");
            }
        }
    }

    private bool IsParameter() => IsKeyword(new List<string> { "int", "char", "boolean" });

    public void CompileSubroutineBody()
    {
        writer.Write("<subroutineBody>");
        WriteSymbol("{");
        CompileVarDec();
        CompileStatements();
        WriteSymbol("}");
        writer.Write("</subroutineBody>");
    }

    public void CompileVarDec()
    {
        if (!IsVar())
        {
            return;
        }

        while (IsVar())
        {
            writer.Write("<varDec>");
            WriteKeyword("var");
            CompileType();  // type
            WriteIdentifier();  // varName
            while (IsSymbol(","))
            {
                WriteSymbol(",");
                WriteIdentifier();  // varName
            }
            WriteSymbol(";");
            writer.Write("</varDec>");
        }
    }

    private bool IsVar() => IsKeyword("var");

    public void CompileStatements()
    {
        writer.Write("<statements>");

        while (CompileAll())
        {
            continue;
        }

        writer.Write("</statements>");
    }

    private bool CompileAll() => CompileLet() || CompileDo() || CompileIf() || CompileReturn() || CompileWhile();

    public bool CompileDo()
    {
        if (!CheckDo())
        {
            return false;
        }

        writer.Write("<doStatement>");
        WriteKeyword("do");
        CompileSubroutineCall();
        WriteSymbol(";");
        writer.Write("</doStatement>");
        return true;
    }

    private bool CheckDo() => IsKeyword("do");

    public bool CompileLet()
    {
        if (!CheckLet())
        {
            return false;
        }

        writer.Write("<letStatement>");
        WriteKeyword("let");
        WriteIdentifier(); // varName
        if (IsSymbol("["))
        {
            WriteSymbol("[");
            CompileExpression();
            WriteSymbol("]");
        }
        WriteSymbol("=");
        CompileExpression();
        WriteSymbol(";");
        writer.Write("</letStatement>");
        return true;
    }

    private bool CheckLet() => IsKeyword("let");

    public bool CompileWhile()
    {
        if (!CheckWhile())
        {
            return false;
        }

        writer.Write("<whileStatement>");
        WriteKeyword("while");
        WriteSymbol("(");
        CompileExpression();
        WriteSymbol(")");
        WriteSymbol("{");
        CompileStatements();
        WriteSymbol("}");
        writer.Write("</whileStatement>");
        return true;
    }

    private bool CheckWhile() => IsKeyword("while");

    public bool CompileReturn()
    {
        if (!CheckReturn())
        {
            return false;
        }

        writer.Write("<returnStatement>");
        WriteKeyword("return");
        if (!IsSymbol(";"))
        {
            CompileExpression();
        }
        WriteSymbol(";");
        writer.Write("</returnStatement>");
        return true;
    }

    private bool CheckReturn() => IsKeyword("return");

    public bool CompileIf()
    {
        if (!CheckIf())
        {
            return false;
        }

        writer.Write("<ifStatement>");
        WriteKeyword("if");
        WriteSymbol("(");
        CompileExpression();
        WriteSymbol(")");
        WriteSymbol("{");
        CompileStatements();
        WriteSymbol("}");
        writer.Write("</ifStatement>");
        return true;
    }

    private bool CheckIf() => IsKeyword("if");

    public void CompileExpression()
    {
        writer.Write("<expression>");
        CompileTerm();
        while (IsOp())
        {
            WriteSymbol(this.tokenizer.GetSymbol());
            CompileTerm();
        }
        writer.Write("</expression>");
    }

    public void CompileTerm()
    {
        writer.Write("<term>");
        if (IsInt()) WriteInt();
        else if (IsString()) WriteString();
        else if (IsKeyword()) WriteKeyword();
        else if (IsSubroutineCall()) CompileSubroutineCall();
        else if (IsIdentifier())
        {
            WriteIdentifier(); // varName
            if (IsSymbol("["))
            {
                WriteSymbol("[");
                CompileExpression();
                WriteSymbol("]");
            }
        }
        else if (IsSymbol("("))
        {
            WriteSymbol("(");
            CompileExpression();
            WriteSymbol(")");
        }
        else if (IsSymbol(new List<string> { "-", "~" }))
        {
            WriteSymbol(this.tokenizer.GetSymbol());
            CompileTerm();
        }
        writer.Write("</term>");
    }

    public void CompileExpressionList()
    {
        writer.Write("<expressionList>");

        if (!IsSymbol(")"))
        {
            CompileExpression();
            while (IsSymbol(","))
            {
                WriteSymbol(",");
                CompileExpression();
            }
        }
        writer.Write("</expressionList>");
    }

    private bool IsSubroutineCall()
    {
        bool flag = IsIdentifier();
        this.tokenizer.Advance();
        flag = flag && IsSymbol(new List<string> { "(", "." });
        this.tokenizer.Back();
        return flag;
    }

    public void CompileSubroutineCall()
    {
        if (!IsSubroutineCall())
        {
            return;
        }
        WriteIdentifier();
        if (this.tokenizer.GetSymbol() == ".")
        {
            WriteSymbol(".");
            WriteIdentifier();
        }
        WriteSymbol("(");
        CompileExpressionList();
        WriteSymbol(")");
    }
}