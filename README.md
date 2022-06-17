# Website monitoring Probe-Generator
Quick and Dirty Generator für blackbox-exporter Prometheus-Operator-Probes.

## Was macht es 
Erzeugt Prometheus-Operator-Probes Manifest-Dateien für ausgewählte Webseiten/Web-Applikationen

Aus folgender Eingabe

```
globals:
  monitoringInstance: k8s01
  team: systeme
  proberUrl: prometheus-blackbox-exporter.witcom-operations:9115
  interval: 60s
  module: http_ssl_2xx
websites:
  - job: witcom-exchange
    instance: wit-ex01-12r2
    targets:
      - https://wit-ex01-12r2.witcom.net
      - https://mail.witcom.de
  - job: witcom-iam
    targets:
      - https://auth.witcom.services
```

wird

```
apiVersion: v1
items:
- apiVersion: monitoring.coreos.com/v1
  kind: Probe
  metadata:
    labels:
      app.kubernetes.io/monitoring-instance: k8s01
      probe: website
    name: web-witcom-exchange-wit-ex01-12r2
  spec:
    interval: 60s
    module: http_ssl_2xx
    prober:
      url: prometheus-blackbox-exporter.witcom-operations:9115
    targets:
      staticConfig:
        labels:
          job: witcom-exchange
          team: devops-team
          probe: website
        static:
        - https://wit-ex01-12r2.witcom.net
        - https://mail.witcom.de
        relabelingConfigs:
        - targetLabel: instance
          replacement: wit-ex01-12r2
        - sourceLabels:
          - __param_target
          targetLabel: target
        - regex: namespace
          action: labeldrop
- apiVersion: monitoring.coreos.com/v1
  kind: Probe
  metadata:
    labels:
      app.kubernetes.io/monitoring-instance: k8s01
      probe: website
    name: web-witcom-iam
  spec:
    interval: 60s
    module: http_ssl_2xx
    prober:
      url: prometheus-blackbox-exporter.witcom-operations:9115
    targets:
      staticConfig:
        labels:
          job: witcom-iam
          team: devops-team
          probe: website
        static:
        - https://auth.witcom.services
        relabelingConfigs:
        - targetLabel: instance
          replacement: witcom-iam
        - sourceLabels:
          - __param_target
          targetLabel: target
        - regex: namespace
          action: labeldrop
kind: List
metadata:
  resourceVersion: ""
  selfLink: ""
```

## Warum
Macht man es richtig, so werden die zu monitorenden Ziele in einer separaten Applikation definiert und per REST-API bereitgestellt. Prometheus würde dann per HTTP-Service-Discovery alle Target ermitteln.

Haben wir nicht -> deswegen diese Poor-Mans-Variante die zumindest die Tipp-Arbeit reduziert

## Format Ziel-Definition

```
# globasle parameter die fuer alle generierten Probes gelten
globals:
  #erzeugt das label monitoringInstance. Relevant für Prometheus-Instanzen mit probeSelector
  monitoringInstance: k8s01
  #erzeugt das label team. Wird genutzt für alerting. (gehoert wo anders hin, das ist aber ein anderes Thema) 
  team: systeme
  #blackbox-exporter URL
  proberUrl: prometheus-blackbox-exporter.witcom-operations:9115
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
