Imports System.Drawing

Partial Public Class MPK_API
    Function GetFocusMetric(imageKey As String, region As Rectangle) As JObject
        Try
            Dim focusMetricValue = ttAPI.GetFocusMetric(imageKey, region)
            Return JSONSingleEntry("FocusMetric", focusMetricValue)
        Catch ex As TrueTestAPIException
            If TypeOf ex Is MeasurementNotFoundException Then
                Return JSONKnownException(ErrorCode.MeasurementNotFound)
            Else
                Return JSONKnownException(ErrorCode.InitializationFailure)
            End If
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function
End Class
