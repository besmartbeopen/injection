# Here you can create play commands that are specific to the module, and extend existing commands
import os
import os.path
import shutil
import time

from play.utils import *

MODULE = 'injection'

# Commands that are specific to your module

COMMANDS = ['injection:ec']

HELP = {
        'injection:ec': 'Update eclipse .classpath file.'
}

def execute(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    play_env = kargs.get("env")

    is_application = os.path.exists(os.path.join(app.path, 'conf', 'application.conf'))
    if is_application:
        app.check()
        app.check_jpda()
    modules = app.modules()
    classpath = app.getClasspath()

    # determine the name of the project
    # if this is an application, the name of the project is in the application.conf file
    # if this is a module, we infer the name from the path
    application_name = app.readConf('application.name')
    vm_arguments = app.readConf('jvm.memory')

    javaVersion = getJavaVersion()
    print "~ using java version \"%s\"" % javaVersion
    if javaVersion.startswith("1.7"):
        # JDK 7 compat
        vm_arguments = vm_arguments +' -XX:-UseSplitVerifier'
    elif javaVersion.startswith("1.8"):
        # JDK 8 compatible
        vm_arguments = vm_arguments +' -noverify'

    if application_name:
        application_name = application_name.replace("/", " ")
    else:
        application_name = os.path.basename(app.path)

    dotClasspath = os.path.join(app.path, '.classpath')

    shutil.copyfile(os.path.join(play_env["basedir"], 'resources/eclipse/.classpath'), dotClasspath)

    playJarPath = os.path.join(play_env["basedir"], 'framework', 'play-%s.jar' % play_env['version'])
    playSourcePath = os.path.join(os.path.dirname(playJarPath), 'src')
    if os.name == 'nt':
        playSourcePath=playSourcePath.replace('\\','/').capitalize()

    cpJarToSource = {}
    lib_src = os.path.join(app.path, 'tmp/lib-src')
    for el in classpath:
        # library sources jars in the lib directory
        if os.path.basename(el) != "conf" and el.endswith('-sources.jar'):
            cpJarToSource[el.replace('-sources', '')] = el

        # pointers to source jars produced by 'play deps'
        src_file = os.path.join(lib_src, os.path.basename(el) + '.src')
        if os.path.exists(src_file):
            f = file(src_file)
            cpJarToSource[el] = f.readline().rstrip()
            f.close()

    javadocLocation = {}
    for el in classpath:
        urlFile = el.replace(r'.jar','.docurl')
        if os.path.basename(el) != "conf" and os.path.exists(urlFile):
            javadocLocation[el] = urlFile

    cpXML = ""
    for el in sorted(classpath):
        if os.path.basename(el) != "conf":
            if el == playJarPath:
                cpXML += '<classpathentry kind="lib" path="%s" sourcepath="%s" />\n\t' % (os.path.normpath(el) , playSourcePath)
            else:
                if cpJarToSource.has_key(el):
                    cpXML += '<classpathentry kind="lib" path="%s" sourcepath="%s"/>\n\t' % (os.path.normpath(el), cpJarToSource[el])
                else:
                    if javadocLocation.has_key(el):
                        cpXML += '<classpathentry kind="lib" path="%s">\n\t\t' % os.path.normpath(el)
                        cpXML += '<attributes>\n\t\t\t'
                        f = file(javadocLocation[el])
                        url = f.readline()
                        f.close()
                        cpXML += '<attribute name="javadoc_location" value="%s"/>\n\t\t' % (url.strip())
                        cpXML += '</attributes>\n\t'
                        cpXML += '</classpathentry>\n\t'
                    else:
                        cpXML += '<classpathentry kind="lib" path="%s"/>\n\t' % os.path.normpath(el)
    if not is_application:
        cpXML += '<classpathentry kind="src" path="src"/>'
    replaceAll(dotClasspath, r'%PROJECTCLASSPATH%', cpXML)

    # generate source path for test folder if one exists
    cpTEST = ""
    if os.path.exists(os.path.join(app.path, 'test')):
        cpTEST += '<classpathentry kind="src" path="test"/>'
    replaceAll(dotClasspath, r'%TESTCLASSPATH%', cpTEST)

    if len(modules):
        lXML = ""
        cXML = ""
        for module in sorted(modules):
            lXML += '<link><name>%s</name><type>2</type><location>%s</location></link>\n' % (os.path.basename(module), os.path.join(module, 'app').replace('\\', '/'))
            if os.path.exists(os.path.join(module, "conf")):
                lXML += '<link><name>conf/%s</name><type>2</type><location>%s/conf</location></link>\n' % (os.path.basename(module), module.replace('\\', '/'))
            if os.path.exists(os.path.join(module, "public")):
                lXML += '<link><name>public/%s</name><type>2</type><location>%s/public</location></link>\n' % (os.path.basename(module), module.replace('\\', '/'))
            cXML += '<classpathentry kind="src" path="%s"/>\n\t' % (os.path.basename(module))
        replaceAll(dotClasspath, r'%MODULES%', cXML)
    else:
        replaceAll(dotClasspath, r'%MODULES%', '')

    print "successfully recreated eclipse classpath, please refresh project"


# This will be executed before any command (new, run...)
def before(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")


# This will be executed after any command (new, run...)
def after(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")

    if command == "new":
        pass
