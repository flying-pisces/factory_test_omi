Imports System.Collections.Concurrent

Friend Interface IResponse
    Function ToByteArray() As Byte()
    Function ToLog() As String
End Interface

Partial Public Class MPK_API

    Private Const cErrorCode As String = "ErrorCode"
    Public Enum ErrorCode
        Success = 0
        Unknown = 1
        InitializationFailure = 2
        ErrorMeasurement = 3
        MeasurementNotFound = 4
        MeasurementSetupNotFound = 5
        ErrorAnalysisParameter = 6
    End Enum

    Private JSONUnknownException As Func(Of JObject) =
        Function()
            Return JSONSingleEntry(cErrorCode, ErrorCode.Unknown)
        End Function

    Private JSONKnownException As Func(Of ErrorCode, JObject) =
        Function(ec)
            Return JSONSingleEntry(cErrorCode, ec)
        End Function

    Private JSONSuccess As Func(Of JObject) =
        Function()
            Return JSONSingleEntry(cErrorCode, ErrorCode.Success)
        End Function

    Private JSONSingleEntry As Func(Of String, String, JObject) =
        Function(key, value)
            Return CommandBuilder.Build(New Dictionary(Of String, String) From {{key, value}}).JObject
        End Function

    Private CalDictionaryParser As Func(Of Dictionary(Of Integer, String), JObject) =
        Function(calDictionary)
            Return CommandBuilder.Build(calDictionary.ToDictionary(Function(k) k.Key.ToString, Function(v) v.Value)).JObject
        End Function

    Private SerialDictionaryParser As Func(Of ConcurrentDictionary(Of Integer, String), JObject) =
        Function(serialDictionary)
            Return CommandBuilder.Build(serialDictionary.ToDictionary(Function(k) k.Key.ToString, Function(v) v.Value)).JObject
        End Function

End Class
