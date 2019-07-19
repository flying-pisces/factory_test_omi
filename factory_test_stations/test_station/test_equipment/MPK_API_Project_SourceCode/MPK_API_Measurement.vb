Partial Public Class MPK_API
    Public Function CaptureMeasurement(measurementSetupName As String, imageKey As String, saveToDatabase As Boolean) As JObject
        Try
            ttAPI.CaptureMeasurement(measurementSetupName, imageKey, saveToDatabase)
            Return JSONSingleEntry("Imagekey", imageKey)
        Catch ex As TrueTestAPIException
            If TypeOf ex Is ErrorMeasurementException Then
                Return JSONKnownException(ErrorCode.ErrorMeasurement)
            Else
                Return JSONUnknownException()
            End If
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function GetMeasurementNames() As List(Of String)
        Return ttAPI.GetMeasurementNames
    End Function

    Public Function FlushMeasurements() As JObject
        ttAPI.FlushMeasurements()
        Return JSONSuccess()
    End Function
End Class
