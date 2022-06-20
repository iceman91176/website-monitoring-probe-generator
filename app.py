import sys
import yaml
import json
import jinja2
import os
from pathlib import Path

def get_global(name,envvar):
    '''Gets property from environment'''
    prop = os.environ.get(envvar)
    if prop is None:
        raise Exception("Property " + name + " could not be set from ENV " + envvar)
    return prop

def get_globals():
    '''Get global configuration from environment variables'''
    default_globals = {"interval":"60s"}
    default_globals["monitoringInstance"] = get_global("monitoringInstance","MONITORING_INSTANCE")
    default_globals["team"] = get_global("team","TEAM")
    default_globals["proberUrl"] = get_global("proberUrl","PROBER_URL")
    default_globals["module"] = get_global("module","MODULE")
    default_globals["proberId"] = get_global("proberId","PROBER_ID")
    default_globals["proberResourceName"] = get_global("proberResourceName","PROBER_RESOURCE_NAME")

    return default_globals

def main():
    '''Render configuration'''
    template_file = Path("./templates/probe.j2")
    variables_file = Path("./data/websites.yaml")

    if variables_file.suffix in [".yml", ".yaml"]:
        with open(variables_file, "r") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
    elif variables_file.suffix == ".json":
        with open(variables_file, "r") as f:
            data = json.load(f)
    else:
        sys.exit(f"Not supported file format: {variables_file.suffix}")

    #set defaults form ENV if not present in data file
    if 'globals' not in data:
        print("Get globals from ENV")
        data["globals"] = get_globals()

    #update missing properties from ENV if possible
    if 'monitoringInstance' not in data["globals"]:
        data["globals"]["monitoringInstance"] = \
          get_global("monitoringInstance","MONITORING_INSTANCE")
    if 'team' not in data["globals"]:
        data["globals"]["team"] = \
          get_global("team","TEAM")
    if 'proberUrl' not in data["globals"]:
        data["globals"]["proberUrl"] = \
          get_global("proberUrl","PROBER_URL")
    if 'proberId' not in data["globals"]:
        data["globals"]["proberId"] = \
          get_global("proberId","PROBER_ID")
    if 'proberResourceName' not in data["globals"]:
        data["globals"]["proberResourceName"] = \
          get_global("proberResourceName","PROBER_RESOURCE_NAME")

    if 'module' not in data["globals"]:
        data["globals"]["module"] = \
          get_global("module","MODULE")

    # Verify template format
    if template_file.suffix != ".j2":
        sys.exit(f"Template file format not supported: {template_file.suffix}")

    # Get the template data from file
    with open(template_file, "r") as f:
        template_data = f.read()

    # Generate template object
    template = jinja2.Template(template_data)

    # Render the template
    configuration_data = template.render(data)

    # Save the configuration to output file
    output_file = "output/probes.yaml"
    with open(output_file, "w") as f:
        f.write(configuration_data)

    print("Created {} File! " .format(output_file))

    print(configuration_data)

    return

if __name__ == "__main__":
    main()
