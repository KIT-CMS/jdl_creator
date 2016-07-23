from __future__ import unicode_literals, print_function

import os
import subprocess
# TODO GUI
# import PyQt4


class CloudSite(object):
    def __init__(self, name=''):
        self.name = name
        self.universe =''
        self.docker_image = ''
        self.requirements =''
        if name == 'condocker':
            self.universe = "docker"
            self.docker_image = "mschnepf/slc6-condocker"
            self.requirements = '(TARGET.CLOUD_SITE == "condocker")'
        elif name == 'ekpcloud':
            self.universe = "vanilla"
            self.requirements = '(TARGET.CLOUD_SITE == "ekpcloud")'

        elif name == 'ekpsupermachines':
            self.universe = "docker"
            self.docker_image = "mschnepf/slc6-condocker"
            self.requirements = '(TARGET.CLOUD_SITE == "ekpsupermachines")'

        elif name == 'bwforcluster':
            self.universe = "vanilla"
            self.requirements = '(TARGET.CLOUD_SITE == "bwforcluster")'

        elif name == 'gridka':
            self.universe = "vanilla"
            self.requirements = '(TARGET.CLOUD_SITE == "gridka")'

        elif name == 'oneandone':
            self.universe = "vanilla"
            self.requirements = '(TARGET.CLOUD_SITE == "oneandone")'
        else:
            self.universe = "docker"
            self.docker_image = "mschnepf/slc6-condocker"
            self.requirements = ""


class JDLCreator(object):
    """Class to create JDL files for EKP HTCondor system."""

    """Lines for output, log and errors."""
    LINE_OUTPUT = "output = out/$(Process).out"
    LINE_ERROR = "error = error/$(Process).err"
    LINE_LOG = "log = log/$(Process).log"

    def __init__(self, site_name="", executable="", wall_time=0, job_folder="",
                 extra_lines="", output_files="", arguments=""):
        # types (str, str, int, str, list, str, list) -> None
        ###
        # public attributes - user is allowed to change these values
        ###

        self.executable = executable

        ###
        # protected attributes - encapsulated by setter/getter/deleter
        ###
        self._cloud_site = CloudSite(site_name.lower())
        self._wall_time = int(wall_time)
        self._memory = 0
        self._job_folder = job_folder
        self._output_files = output_files
        self._input_files = ""
        self._remote_job = False
        if len(extra_lines) > 0:
            self._extra_lines = extra_lines
        else:
            self._extra_lines = []
        if len(arguments) > 0:
            self._arguments = arguments
        else:
            self._arguments = []
        ###
        # private attributes - only we need them
        ###
        self.__JDLFilename = None

    ###
    # Allow usage as context manager
    # statement "with JDLCreator('docker') as JDL:"
    ###
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # propagate exceptions
        return False

    ###
    # Properties, setters, deleters
    ###
    @property
    def job_folder(self):
        # type: () -> str
        return self._job_folder

    @job_folder.setter
    def job_folder(self, folder):
        # type: (str) -> None
        """Defines a folder for JDL file, logs and script"""
        self._job_folder = folder

    def SetFolder(self, folder):
        # type: (str) -> None
        """Defines a folder for JDL file, logs and script"""
        self._job_folder = folder

    def SetExecutable(self, exe):
        # type (str) -> None
        """Defines executable"""
        self.executable = exe


    @property
    def extra_lines(self):
        """List of extra lines."""
        return self._extra_lines

    @extra_lines.setter
    def extra_lines(self, line):
        self._extra_lines.append(str(line))

    @extra_lines.deleter
    def extra_lines(self):
        self._extra_lines = []

    def AddExtraLines(self, line):
        # type: (str) -> None
        self._extra_lines.append(str(line))

    def ClearExtraLines(self, line):
        # type: (str) -> None
        self._extra_lines = []

    @property
    def requirements(self):
        # type () -> str
        """Requirement string to only dispatch the job to specific sites."""
        return self._cloud_site.requirements

    @requirements.setter
    def requirements(self, requirement_):
        # type (str) -> None
        """Add Requirments string."""
        if isinstance(requirement_, list):
            for line in requirement_:
                # recursive call on itself
                self.requirements = line
        # check data-type
        elif isinstance(requirement_, str):
            if len(self.requirements) > 0:
                self._cloud_site.requirements += " && ( " + requirement_ + " ) "
            else:
                self._cloud_site.requirements += " ( " + requirement_ + " ) "
        else:
            raise TypeError("Argument is not a string")

    @property
    def wall_time(self):
        # type: () -> int
        """Job run time in seconds."""
        return self._wall_time

    @wall_time.setter
    def wall_time(self, time):
        """Expected maximum job run time (upper limit). Format: seconds"""
        # type: (int) -> None
        self._wall_time = time

    def SetWalltime(self, time):
        """Expected maximum job run time (upper limit). Format: seconds"""
        # type: (int) -> None
        self._wall_time = time


    @property
    def memory(self):
        """Requested momory in MB"""
        return self._memory

    @memory.setter
    def memory(self, memory_):
        # type: (int) -> None
        """Expected maximum memory (upper limit) in MB"""
        self._memory = memory_

    def SetMemory(self, memory_):
        # type: (int) -> None
        """Expected maximum memory (upper limit) in MB"""
        self._memory = memory_



    @property
    def arguments(self):
        # type: () -> list
        return self._arguments

    @arguments.setter
    def arguments(self, argument):
        # type (str, int, float) -> None
        """Set list of arguments for submit"""
        if isinstance(argument, list):
            for line in argument:
                self.arguments = line
        elif isinstance(argument, (str, int, float)):
            self._arguments.append(str(argument))
        else:
            raise TypeError("Argument is not a string or a number")

    @arguments.deleter
    def arguments(self):
        # type: () -> None
        self._arguments = []

    def SetArguments(self, argument):
        # type (str, int, float) -> None
        """Set list of arguments for submit"""
        if isinstance(argument, list):
            for line in argument:
                self.arguments = line
        elif isinstance(argument, (str, int, float)):
            self._arguments.append(str(argument))
        else:
            raise TypeError("Argument is not a string or a number")


    @property
    def image(self):
        # type: () -> str
        return self._cloud_site.docker_image

    @image.setter
    def image(self, image_name):
        # type: (str) -> None
        if self._cloud_site.universe == "docker":
            self._cloud_site.docker_image = image_name
        else:
            raise AttributeError("You are not in a docker universe. :-(")

    def ChangeImage(self, image_name):
        # type: (str) -> None
        print(self._cloud_site.docker_image)
        print(str(self._cloud_site.universe))
        if self._cloud_site.universe == "docker":
            self._cloud_site.docker_image = image_name
        else:
            raise AttributeError("You are not in a docker universe. :-(")


    

    @property
    def output_files(self):
        # type: () -> str
        """Files or directories which should be transferred back by HTCondor."""
        return self._output_files

    @output_files.setter
    def output_files(self, file_string):
        # type: (str) -> None
        self._output_files = file_string

    def SetOutputFiles(self, file_string):
        # type: (str) -> None
        self._output_files = file_string

    @property
    def input_files(self):
        # type: () -> str
        """Files or directories which should be transferred to workernode by HTCondor."""
        return self._input_files

    @input_files.setter
    def input_files(self, file_string):
        # type: (str) -> None
        self._input_files = file_string

    def SetInputFiles(self, file_string):
        # type: (str) -> None
        self._input_files = file_string



    @property
    def remote_job(self):
        # type: () -> boolean
        """Define if an job can run remote"""
        return self._remote_job

    @remote_job.setter
    def remote_job(self, value):
        # type: (boolean) -> None
        self._remote_job = value

    def SetRemoteJob(self, value):
        # type: (boolean) -> None
        self._remote_jobs = value


    def print_stats(self):
        # type: () -> None
        """Print current attribute values to screen."""
        print(self._cloud_site.universe)
        if self._cloud_site.universe == "docker":
            print(self._cloud_site.docker_image)
        if len(self.executable) > 0:
            print(self.executable)

        print(self.LINE_OUTPUT)
        print(self.LINE_ERROR)
        print(self.LINE_LOG)
        print(self.requirement)

        if len(self.arguments) > 0:
            print('Arguments: ')
            [print(line) for line in self.arguments]

    def __get_JDL_content(self):
        # type: () -> list
        """Create JDL content(!). This does NOT create the JDL file.
        
         Put all attributes in a list of lines for the JDL file.
         """
        jdl_content = list()

        if len(self.executable) is 0:
            raise ValueError("No executable set!")
        exe = self.executable.split('/')[-1]  # remove path to executable

        jdl_content.append("universe = " + self._cloud_site.universe)

        if self._cloud_site.universe == "docker":
            jdl_content.append("docker_image = " + str(self._cloud_site.docker_image))
            # do docker stuff for exe
            jdl_content.append("executable = ./" + exe)
            jdl_content.append("should_transfer_files = YES")
            if self._input_files != "":
                jdl_content.append("transfer_input_files = " + self.executable+','+self._input_files)
            else:
                jdl_content.append("transfer_input_files = " + self.executable)

        else:
            jdl_content.append("executable = " + exe)

        # add log files
        jdl_content.append(self.LINE_OUTPUT)
        jdl_content.append(self.LINE_ERROR)
        jdl_content.append(self.LINE_LOG)

        # add line to transfer files back
        jdl_content.append('transfer_output_files = "' + self.output_files + '"')

        # add environments
        jdl_content.append('getenv = True')

        # add remote job
        if self._remote_job is True:
            jdl_content.append("remote_job = true")


        # add requirements
        if len(self._cloud_site.requirements) > 0:
            jdl_content.append("requirements = " + self._cloud_site.requirements)
        else:
            print("Warning: You didn't set requirements! Please add '.requirements = str'")

        # add wall_time, if set
        if self._wall_time > 0:
            jdl_content.append("+RequestWalltime = " + str(self._wall_time))
        else:
            print("Warning: You didn't set a walltime! Please add ' .wall_time = int'  in seconds")

        # add memeory, if set
        if self._memory > 0:
            jdl_content.append("RequestMemory = " + str(self._memory))
        else:
            print("Warning: You didn't set the requested memory! Please add '.memory = int' in MB")


        # add extra lines to JDL
        if len(self.extra_lines) > 0:
            for line in self.extra_lines:
                jdl_content.append(line)

        jdl_content.append("queue arguments from arguments.txt")

        return jdl_content

    def PrintJDL(self):
        """Output JDL content to screen."""
        [print(line) for line in self.__get_JDL_content()]

    def WriteJDL(self, exe='', arguments=''):
        """Create folder (if set) and  write JDLFile, argument list file,

            copy job in the folder"""
        if len(exe) > 0:
            self.executable = exe
        if len(arguments) > 0:
            self.arguments = arguments

        jdl_content = self.__get_JDL_content()

        if hasattr(self, 'job_folder'):
            command = "mkdir -p " + self.job_folder
            os.system(command)
            command = "mkdir -p " + self.job_folder + "/log"
            os.system(command)
            command = "mkdir -p " + self.job_folder + "/out"
            os.system(command)
            command = "mkdir -p " + self.job_folder + "/error"
            os.system(command)
            # copy script to folder
            if os.path.isfile(self.executable):
                command = "cp " + self.executable + " " + self.job_folder
                os.system(command)
                command = "chmod +x " + self.job_folder + "/" + self.executable
                os.system(command)
        else:
            os.system("mkdir -p log")
            os.system("mkdir -p out")
            os.system("mkdir -p error")
            command = "chmod +x " + self.executable
            os.system(command)

        # create JDL file
        if len(self.job_folder) > 0:
            self.__JDLFilename = self.job_folder + '/'
        else:
            self.__JDLFilename = ""
        self.__JDLFilename += ('JDL_' +
                               str(self.executable).split('/')[-1].rsplit('.')[0])

        with open(self.__JDLFilename, 'w') as file:
            for line in jdl_content:
                line += u'\n'
                file.write(line)

        # create argument list file
        if len(self.job_folder) > 0:
            arguments_filename = self.job_folder + '/'
        else:
            arguments_filename = ""
        arguments_filename += 'arguments.txt'

        with open(arguments_filename, 'w') as file:
            for index, line in enumerate(self.arguments):
                if index < len(self.arguments):
                    line += '\n'
                file.write(line)

        if len(self.job_folder) > 0:
            print("wrote JDL file: " + self.__JDLFilename + " in folder " + self.job_folder)
        else:
            print("wrote JDL file: " + self.__JDLFilename)

    def Submit(self, exe='', arguments='', remove_after_start=True):
        ###
        # check input
        ###
        if len(exe) > 0:
            self.executable = exe
        if len(arguments) > 0:
            self.arguments = arguments
        # remove JDL file when user only starts one job with one file
        if len(self.arguments) > 1 and remove_after_start is True:
            remove_after_start = False

        self.WriteJDL()

        ###
        # call submit
        ###
        main_path = ''
        if len(self.job_folder) > 0:  # when folder is set, jump in folder
            main_path = os.getcwd()
            os.chdir(self.job_folder)

        command = "condor_submit " + self.__JDLFilename.split('/')[-1]
        print(command)
        if subprocess.call(command.split(), shell=False):
            raise RuntimeError("submit failed! Check your configuration")

        # jump back
        if len(main_path) > 0:
            os.chdir(main_path)

        if remove_after_start is True:
            command = "rm " + self.__JDLFilename
            os.system(command)
