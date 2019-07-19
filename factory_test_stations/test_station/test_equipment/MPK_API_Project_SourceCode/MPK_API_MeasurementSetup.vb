Imports System.Drawing

Partial Public Class MPK_API
    Public Function CreateMeasurementSetup(description As String, redExposure As Single, greenExposure As Single, blueExposure As Single, xbExposure As Single,
                                           focusDistance As Single, lensAperture As Single, autoAdjustExposure As Boolean, subframe As Rectangle) As JObject

        Try
            ttAPI.CreateMeasurementSetup(description, redExposure, greenExposure, blueExposure, xbExposure, focusDistance, lensAperture, autoAdjustExposure, subframe)
            Return JSONSuccess()
        Catch ex As InitializationException
            Return JSONKnownException(ErrorCode.InitializationFailure)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function GetMeasurementSetupNames() As List(Of String)
        Return ttAPI.GetMeasurementSetupNames
    End Function

    Public Function SetCalibrations(measurementSetupName As String, colorCalibrationID As Integer, imageScaleID As Integer, colorShiftID As Integer) As JObject
        Try
            ttAPI.SetCalibrations(measurementSetupName, colorCalibrationID, imageScaleID, colorShiftID)
            Return JSONSuccess()
        Catch ex As MeasurementSetupNotFoundException
            Return JSONKnownException(ErrorCode.MeasurementSetupNotFound)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function GetFlatFieldCalibrationList() As JObject
        Try
            Return CalDictionaryParser(ttAPI.GetFlatFieldCalibrationList())
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function GetColorCalibrationList() As JObject
        Try
            Return CalDictionaryParser(ttAPI.GetColorCalibrationList())
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function GetImageScaleCalibrationList() As JObject
        Try
            Return CalDictionaryParser(ttAPI.GetImageScaleCalibrationList())
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Public Function GetColorShiftCalibrationList() As JObject
        Try
            Return CalDictionaryParser(ttAPI.GetColorShiftCalibrationList())
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Function FlushMeasurementSetups() As JObject
        ttAPI.FlushMeasurementSetups()
        Return JSONSuccess()
    End Function
End Class
