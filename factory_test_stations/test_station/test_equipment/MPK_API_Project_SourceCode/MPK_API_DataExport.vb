Partial Public Class MPK_API
    Public Function ExportData(imageHandle As String, path As String, fileName As String) As JObject
        Try
            ttAPI.ExportData(imageHandle, path, fileName)
            Return JSONSuccess()
        Catch ex As TrueTestAPIException
            Return JSONKnownException(ErrorCode.MeasurementNotFound)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function
End Class
