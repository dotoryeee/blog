provider "helm" {
  kubernetes {
    config_path = module.eks.kubeconfig_filename
  }
}

resource "helm_release" "efk" {
  name      = "efk"
  chart     = "elastic/elasticsearch"
  namespace = "kube-system"

  set {
    name  = "global.kibanaEnabled"
    value = "true"
  }

  set {
    name  = "global.fluentdEnabled"
    value = "true"
  }
}

