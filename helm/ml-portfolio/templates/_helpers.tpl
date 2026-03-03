{{/*
ML Portfolio Helm Chart — Template Helpers
*/}}

{{- define "ml-portfolio.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ml-portfolio.labels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "ml-portfolio.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ml-portfolio.imageRef" -}}
{{ .Values.registry.url }}/{{ .image }}
{{- end -}}
