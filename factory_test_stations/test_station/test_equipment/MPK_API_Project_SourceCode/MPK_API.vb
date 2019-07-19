Public Class MPK_API

    Private ttAPI As TT_API
    Sub New()
        ttAPI = New TT_API
    End Sub

    Public Function InitializeCamera(cameraSerial As String, showFeedbackUI As Boolean, useLogging As Boolean) As JObject
        Try
            ttAPI.InitializeTrueTest(cameraSerial, showFeedbackUI, useLogging)
            Return JSONSuccess()
        Catch ex As TrueTestAPIException
            Return JSONKnownException(ErrorCode.InitializationFailure)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function EquipmentReady() As JObject
        Try
            ttAPI.IsEquipmentReady()
            Return JSONSuccess()
        Catch ex As TrueTestAPIException
            Return JSONKnownException(ErrorCode.InitializationFailure)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function CloseCommunication() As JObject
        Try
            ttAPI.CloseCommunication()
            Return JSONSuccess()
        Catch ex As TrueTestAPIException
            Return JSONUnknownException()
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function CloseCommunicationAndReinitializeCamera(cameraSerial As String, showFeedbackUI As Boolean, useLogging As Boolean) As JObject
        Try
            ttAPI.CloseCommunicationAndReinitializeCamera(cameraSerial, showFeedbackUI, useLogging)
            Return JSONSuccess()
        Catch ex As InitializationException
            Return JSONKnownException(ErrorCode.InitializationFailure)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Function GetCameraSerial() As JObject
        Try
            Return JSONSingleEntry("CameraSerial", ttAPI.GetCameraSerial())
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Function GetTrueTestApiVersionInfo() As JObject
        Try
            Return JSONSingleEntry("TrueTestApiVersionInfo", ttAPI.GetTrueTestApiVersionInfo())
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Function GetMpkApiVersionInfo() As JObject
        Try
            Return JSONSingleEntry("MpkApiVersionInfo", ttAPI.GetMpkApiVersionInfo())
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

End Class
