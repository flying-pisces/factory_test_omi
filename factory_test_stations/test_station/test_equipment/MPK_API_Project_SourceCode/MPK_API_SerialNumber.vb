Partial Public Class MPK_API
    Public Function SetSerialNumber(serial As String, channel As Integer) As JObject
        Try
            ttAPI.SetSerialNumber(serial, channel)
            Return JSONSuccess()
        Catch ex As TrueTestAPIException
            Return JSONKnownException(ErrorCode.Unknown)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function ReadSerialNumbers(channel As Integer) As JObject
        Try
            Dim serial = ttAPI.ReadSerialNumbers(channel)
            Return JSONSingleEntry(String.Format("Serial for Channel {0}", channel), serial)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function FlushSerialNumbers() As Boolean
        Return ttAPI.FlushSerialNumbers()
    End Function
End Class
