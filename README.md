# Website monitoring Probe-Generator
Quick and Dirty Generator für blackbox-exporter Prometheus-Operator-Probes.

## Was macht es 
Erzeugt eine Prometheus-Operator-Probe Manifest-Datei für ausgewählte Webseiten/Web-Applikationen

Aus folgender Eingabe

```
globals:
  monitoringInstance: k8s01
  team: devops-team
  proberResourceName: generic-website-prober
  proberId: an-external-prober
  proberUrl: prometheus-blackbox-exporter.witcom-operations:9115
  module: http_ssl_2xx
  interval: 60s
websites:
  - job: witcom-exchange
    #overrides globals.module
    module: a-funny-module
    #needed if there are multiple instances for the same job, eg. two exchange-servers
    instance: wit-ex01-12r2
    targets:
      - url1
      - url2
  - job: witcom-iam
    targets:
      - https://auth.witcom.services
```

wird

```
apiVersion: monitoring.coreos.com/v1
kind: Probe
metadata:
  labels:
    app.kubernetes.io/monitoring-instance: k8s01
    probe: website
  name: generic-website-prober2
spec:
  interval: 60s
  prober:
    url: prometheus-blackbox-exporter.witcom-operations:9115
  targets:
    staticConfig:
      labels:
        probe: website
      relabelingConfigs:
      #set module
      - sourceLabels:
        - __param_target
        regex: "([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@(.*)" # module@probe@jobname@instance@team@target-url
        targetLabel: __param_module
        replacement: "${1}"
      #set probe-label
      - sourceLabels:
        - __param_target
        regex: "([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@(.*)" # module@probe@jobname@instance@team@target-url
        targetLabel: prober
        replacement: "${2}"
      #set job-label
      - sourceLabels:
        - __param_target
        regex: "([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@(.*)" # module@probe@jobname@instance@team@target-url
        targetLabel: job
        replacement: "${3}"
      #set instance-label
      - sourceLabels:
        - __param_target
        regex: "([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@(.*)" # module@probe@jobname@instance@team@target-url
        targetLabel: instance
        replacement: "${4}"
      #set team-label
      - sourceLabels:
        - __param_target
        regex: "([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@(.*)" # module@probe@jobname@instance@team@target-url
        targetLabel: team
        replacement: "${5}"
      #set target-label
      - sourceLabels:
        - __param_target
        regex: "([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@([\\w\\d_\\-]+)@(.*)" # module@probe@jobname@instance@team@target-url
        targetLabel: target
        replacement: "${6}"
      #set target-url
      - sourceLabels:
        - target
        targetLabel: __param_target
      static:
      - a-funny-module@an-external-prober@witcom-exchange@wit-ex01-12r2@devops-team@url1
      - a-funny-module@an-external-prober@witcom-exchange@wit-ex01-12r2@devops-team@url2
      - http_ssl_2xx@an-external-prober@witcom-iam@witcom-iam@devops-team@https://auth.witcom.services
```

## Warum
Macht man es richtig, so werden die zu monitorenden Ziele in einer separaten Applikation definiert und per REST-API bereitgestellt. Prometheus würde dann per HTTP-Service-Discovery alle Target ermitteln.

Haben wir nicht -> deswegen diese Poor-Mans-Variante die zumindest die Tipp-Arbeit reduziert

## Format Ziel-Definition

```
# globale parameter die fuer alle generierten Probes gelten
globals:
  # erzeugt das label monitoringInstance. Relevant für Prometheus-Instanzen mit probeSelector
  monitoringInstance: k8s01
  # erzeugt das label team. Wird genutzt für alerting. (gehoert wo anders hin, das ist aber ein anderes Thema) 
  team: systeme
  # blackbox-exporter URL
  proberUrl: prometheus-blackbox-exporter.witcom-operations:9115
  # erzeugt das Label prober, welches eine Differenzierung nach Prober ermöglicht. z.B. für Websiten die von einem internem und einem externen Exporter abgefragt werden
  proberId: website-prober
  # Name der erzeugten K8S Resource
  proberResourceName: 
  interval: 60s
  # blackbox-exporter modul, welches per Default von allen Probes genutzt wird
  module: http_ssl_2xx
# liste der probe-definitionen
websites:
    # Aufgabe/job der zu ueberwachenden Website/applikation, sinnvoll fuer gruppiereungen, auswertungen, etc.
    # erzeugt das label "job"
  - job: witcom-exchange
    # gibt es verschiedene Instanzen die den Jobn ausfuehren ? Hierueber erfolgt eine Differenzierung unterschiedlicher instanzen
    # erzeugt das intance-label. Kann weggelassen werden, dann wird der job-name verwendet 
    instance: wit-ex01-12r2
    # liste aller Target-Urls die vom blackbox-exporter aufgerufen werden    
    targets:
      - https://wit-ex01-12r2.witcom.net
      - https://mail.witcom.de
  # naechste definition    
  - job: witcom-iam
    targets:
      - https://auth.witcom.services
```

## Requirements
Python > 3.8

## Docker
### S2I
Vorraussetzungen

* s2i installiert
* Zugiff auf RedHat UBI Images

Dann einfach nur ./build_docker.sh REPO-NAME ausführen, das Image wird dann nach REPO-NAME/prometheus/website-monitoring-probe-generator gepushed

### Ausführen
Input-Spezifikationen ablegen , z.B. unter /tmp/generator

```
docker run -v "/tmp/generator:/opt/app-root/src/data" REPO-NAME/prometheus/website-monitoring-probe-generator:latest
```
