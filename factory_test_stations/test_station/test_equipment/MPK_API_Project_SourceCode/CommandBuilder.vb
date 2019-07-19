Imports System.Text

Class JObjectWrapper
    Implements IResponse

    Public Sub New(jsonObject As JObject)
        JObject = jsonObject
    End Sub

    Public Sub New(jsonString As String)
        JObject = JObject.Parse(jsonString)
    End Sub

    Public Property JObject() As JObject

    Public Function ToByteArray() As Byte() Implements IResponse.ToByteArray
        If JObject Is Nothing Then Return Nothing

        Return Encoding.UTF8.GetBytes(JObject.ToString().Replace(vbCrLf, ""))
    End Function

    Public Function ToLog() As String Implements IResponse.ToLog
        Return JObject.ToString().Replace(vbCrLf, "")
    End Function

End Class

Class ByteArrayWrapper
    Implements IResponse
    Public Sub New(jsonObject As JObject)
        data = Encoding.UTF8.GetBytes(jsonObject.ToString().Replace(vbCrLf, ""))
    End Sub

    Public Sub New(dataString As String)
        data = Encoding.UTF8.GetBytes(dataString)
    End Sub

    Public Sub New(byteArray As Byte())
        data = byteArray
    End Sub

    Private data As Byte()

    Public Function ToByteArray() As Byte() Implements IResponse.ToByteArray
        Return data
    End Function

    Public Function ToLog() As String Implements IResponse.ToLog
        Return String.Format("Byte Array: length {0}", data.Length)
    End Function
End Class

Friend NotInheritable Class CommandBuilder
    Shared Function Build(items As Dictionary(Of String, String)) As JObjectWrapper
        Dim response = New StringBuilder()

        response.Append("{")
        response.Append(String.Join(",", From i In items Select String.Format("""{0}"":""{1}""", i.Key, i.Value)))
        response.Append("}")

        Return New JObjectWrapper(response.ToString())
    End Function
End Class
