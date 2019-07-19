Partial Public Class MPK_API
    Function PrepareForRun() As JObject
        Try
            ttAPI.PrepareForRun()
            Return JSONSuccess()
        Catch ex As TrueTestAPIException
            Return JSONUnknownException()
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function

    Private lastResults As List(Of String)
    Function GetLastResults() As List(Of String)
        Return lastResults
    End Function

    Function RunAnalysisByName(analysisName As String, imageKey As String, xmlParameterSet As String) As JObject
        Return RunAnalysisByName(analysisName, {imageKey}, xmlParameterSet)
    End Function

    Function RunAnalysisByName(analysisName As String, imageKeys() As String, xmlParameterSet As String) As JObject
        Try
            lastResults = ttAPI.RunAnalysisByName(analysisName, imageKeys, xmlParameterSet)
            Return JSONSuccess()
        Catch ex As ParameterException
            Return JSONKnownException(ErrorCode.ErrorAnalysisParameter)
        Catch ex As Exception
            Return JSONUnknownException()
        End Try
    End Function
End Class
