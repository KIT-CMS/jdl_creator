from __future__ import unicode_literals, print_function

import os
import shutil
import stat
import subprocess


# TODO GUI
# import PyQt4


class CloudSite(object):
    def __init__(self, name=''):
        self.name = name
        self.universe = ''
        self.docker_image = ''
        self.requirements = ''
        if name == 'condocker':
            self.universe = 'docker'
            self.docker_image = 'mschnepf/slc6-condocker'
            self.requirements = '(TARGET.CLOUDSITE == "condocker")'

        elif name == 'docker':
            self.universe = 'docker'
            self.docker_image = 'mschnepf/slc6-condocker'

        elif name == 'ekpsupermachines':
            self.universe = 'docker'
            self.docker_image = 'mschnepf/slc6-condocker'
            self.requirements = '(TARGET.CLOUDSITE == "ekpsupermachines")'

        elif name == 'bwforcluster':
            self.universe = 'vanilla'
            self.requirements = '(TARGET.CLOUDSITE == "bwforcluster")'

        elif name == 'oneandone':
            self.universe = 'vanilla'
            self.requirements = '(TARGET.CLOUDSITE == "oneandone")'
        else:
            self.universe = 'vanilla'
            self.requirements = ''


class JDLCreator(object):
    """Class to create JDL files for EKP HTCondor system."""
    """Lines for output, log and errors."""
    LINE_OUTPUT = 'output = out/$(Process).out'
    LINE_ERROR = 'error = error/$(Process).err'
    LINE_LOG = 'log = log/$(Process).log'

    def __init__(self, site_name='', executable='', wall_time=0, job_folder='.',
                 extra_lines='', arguments=''):
        # types (str, str, int, str, list, str, list) -> None
        """Class to create JDL files for EKP HTCondor system."""

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
        self._disk_space = 0
        self._job_folder = job_folder
        self._output_files = []
        self._input_files = []
        self._remote_job = False
        self._cpus = 1
        self._accounting_group = ""
        self._cache_files = []
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
        self.job_folder = folder

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
        self.extra_lines = line

    def ClearExtraLines(self):
        # type: (str) -> None
        del self.extra_lines

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
                self._cloud_site.requirements += ' && ( %s )' % requirement_
            else:
                self._cloud_site.requirements += ' ( %s ) ' % requirement_
        else:
            raise TypeError('Argument is not a string')

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
        self.wall_time = time

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
        self.memory = memory_

    @property
    def cpus(self):
        """Get Requested number of cores"""
        return self._cpu

    @cpus.setter
    def cpus(self, cpus_):
        # type: (int) -> None
        """Set Requested number of cores"""
        self._cpus = cpus_

    def SetCpu(self, cpus_):
        # type: (int) -> None
        """Set requested number of cores"""
        self.cpus = cpus_

    @property
    def disk_space(self):
        """Requested disk space in MB"""
        return self._disk_space

    @memory.setter
    def disk_space(self, disk_space_):
        # type: (int) -> None
        """Expected maximum disk_space (upper limit) in MB"""
        self._disk_space = disk_space_

    def SetMemory(self, disk_space_):
        # type: (int) -> None
        """Expected maximum disk space (upper limit) in MB"""
        self.memory = disk_space_


    @property
    def accounting_group(self):
        """Get accounting group"""
        return self._cpu

    @accounting_group.setter
    def accounting_group(self, accounting_group_):
        # type: (int) -> None
        """Set accounting group"""
        self._accounting_group = accounting_group_

    def SetAccounting_group(self, accounting_group_):
        # type: (int) -> None
        """Set accounting group"""
        self.accounting_group = accounting_group_


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
        elif isinstance(argument, (str, int, float, unicode)):
            self._arguments.append(str(argument))
        else:
            raise TypeError('Argument is not a string or a number')

    @arguments.deleter
    def arguments(self):
        # type: () -> None
        self._arguments = []

    def SetArguments(self, argument):
        # type (str, int, float) -> None
        """Set list of arguments for submit"""
        self.arguments = argument

    @property
    def image(self):
        # type: () -> str
        return self._cloud_site.docker_image

    @image.setter
    def image(self, image_name):
        # type: (str) -> None
        if self._cloud_site.universe == 'docker':
            self._cloud_site.docker_image = image_name
        else:
            raise AttributeError('You are not in a docker universe. :-(')

    def ChangeImage(self, image_name):
        # type: (str) -> None
        self.image = image_name

    @property
    def output_files(self):
        # type: () -> str
        """Files or directories which should be transferred back by HTCondor."""
        return ','.join(self._output_files)

    @output_files.setter
    def output_files(self, file_string):
        # type: (str) -> None
        if isinstance(file_string, list):
            for line in file_string:
                self._output_files.append(line)
        elif isinstance(file_string, (str, int, float)):
            self._output_files.append(file_string)
        else:
            raise TypeError('Output file is not a string or a number.')

    def SetOutputFiles(self, file_string):
        # type: (str) -> None
        self.output_files = file_string

    @property
    def input_files(self):
        # type: () -> str
        """Files or directories which should be transferred to workernode by HTCondor."""
        return ','.join(self._input_files)

    @input_files.setter
    def input_files(self, file_string):
        # type: (str) -> None
        if isinstance(file_string, list):
            for line in file_string:
                self._input_files.append( line)
        elif isinstance(file_string, (str, unicode)):
            self._input_files.append(file_string)
        else:
            raise TypeError('Input file is not a string or a number.')

    def SetInputFiles(self, file_string):
        # type: (str) -> None
        self.input_files = file_string

    @property
    def cache_files(self):
        # type: () -> str
        """Files which should be cached with th HTDA caching."""
        return ','.join(self._cache_files)

    @input_files.setter
    def cache_files(self, file_string):
        # type: (str) -> None
        if isinstance(file_string, list):
            for line in file_string:
                self._cache_files.append(line)
        elif isinstance(file_string, (str, unicode)):
            self._cache_files = file_string
        else:
            raise TypeError('Cache file is not a string.')

    def SetCacheFiles(self, file_string):
        # type: (str) -> None
        self.cache_files = file_string


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
        self.remote_job = value

    def print_stats(self):
        # type: () -> None
        """Print current attribute values to screen."""
        print(self._cloud_site.universe)
        if self._cloud_site.universe == 'docker':
            print(self._cloud_site.docker_image)
        if len(self.executable) > 0:
            print(self.executable)

        print(self.LINE_OUTPUT)
        print(self.LINE_ERROR)
        print(self.LINE_LOG)
        print(self.requirements)

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
            raise ValueError('No executable set!')
        exe = self.executable.split('/')[-1]  # remove path to executable

        jdl_content.append('universe = %s' % self._cloud_site.universe)

        if self._cloud_site.universe == 'docker':
            jdl_content.append('docker_image = %s' % self.image)
            # do docker stuff for exe
            jdl_content.append('executable = ./%s' % exe)
            self.input_files = '%s' % exe
        else:
            jdl_content.append('executable = %s' % exe)

        # add log files
        jdl_content.append(self.LINE_OUTPUT)
        jdl_content.append(self.LINE_ERROR)
        jdl_content.append(self.LINE_LOG)

        # Input and output files
        if len(self._input_files) > 0 or len(self._output_files) > 0:
            jdl_content.append('should_transfer_files = YES')
        if len(self._input_files) == 1:
            print(self._input_files)
            jdl_content.append('transfer_input_files = %s' % self._input_files[0])
        if len(self._input_files) > 1:
            filelist =""
            for line in self._input_files:
                filelist+=line
                filelist+=', '
            jdl_content.append('transfer_input_files = %s' % filelist[:-2])
        if len(self._output_files) == 1:
            jdl_content.append('transfer_output_files = %s' % self._output_files[0])
        elif len(self._output_files) > 1:
            filelist =""
            for line in self._output_files:
                filelist+=line
                filelist+=', '
            jdl_content.append('transfer_output_files = %s' % filelist[:-2])
        else:        
            jdl_content.append('transfer_output_files = ""')

        # Cache files 
        if len(self._cache_files) == 1:
            jdl_content.append('+Input_Files = "%s"' % self._cache_files[0])
        if len(self._cache_files) > 1:
            filelist =""
            for line in self._cache_files:
                filelist+=line
                filelist+=', '
            jdl_content.append('+Input_Files = "%s"' % filelist[:-2])
       
        # add environment variables
        jdl_content.append('getenv = True')

        # add remote job
        if self._remote_job is True:
            jdl_content.append('+RemoteJob = True')

        # add requirements
        if len(self._cloud_site.requirements) > 0:
            jdl_content.append('Requirements = %s' % self._cloud_site.requirements)
        else:
            print('Warning: You did not set requirements! Please add ".requirements = str"')

        # add wall_time, if set
        if self._wall_time > 0:
            jdl_content.append('+RequestWalltime = %d' % self._wall_time)
        else:
            print('Warning: You did not set a walltime! Please add ".wall_time = int" in seconds')

        # add memory, if set
        if self._memory > 0:
            jdl_content.append('RequestMemory = %d' % self._memory)
        else:
            print('Warning: You did not set the requested memory! Please add ".memory = int" in MB')
        
        # add cpus, if bigger than 1
        if self._cpus > 1:
            jdl_content.append('request_cpus = %d' % self._cpus)

        if self._disk_space > 0:
            jdl_content.append('request_disk = %d' % (1024 * self._disk_space))

        # add accounting group, if set
        if self._accounting_group is not "":
            jdl_content.append('accounting_group = %s' % self._accounting_group)
        else:
            print('Warning: You did not set the accounting group! Please add ".accounting_group = str"')



        # add extra lines to JDL
        if len(self.extra_lines) > 0:
            for line in self.extra_lines:
                jdl_content.append(line)

        jdl_content.append('queue arguments from arguments.txt')

        return jdl_content

    def PrintJDL(self):
        """Output JDL content to screen."""
        [print(line) for line in self.__get_JDL_content()]

    def WriteJDL(self, exe='', arguments=''):
        """Create job_folder (if set) and  write JDLFile & argument list file; also copies job in the folder"""
        if len(exe) > 0:
            self.executable = exe
        if len(arguments) > 0:
            self.arguments = arguments

        jdl_content = self.__get_JDL_content()

        if hasattr(self, 'job_folder'):
            # "else" is not needed, since we start with default folder "."
            if not os.path.exists(self.job_folder):
                os.makedirs(self.job_folder)
                os.makedirs('%s/log' % self.job_folder)
                os.makedirs('%s/out' % self.job_folder)
                os.makedirs('%s/error' % self.job_folder)
            # copy script to folder
            if os.path.isfile(self.executable) and self.job_folder != '.':
                shutil.copy(self.executable, self.job_folder)
                # make sure the file is executable
                os.chmod('%s/%s' % (self.job_folder, self.executable.split('/')[-1]), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        # create JDL file
        self.__JDLFilename = '%s/%s.jdl' % (self.job_folder, str(self.executable).split('/')[-1].rsplit('.')[0])

        with open(self.__JDLFilename, 'w') as file:
            for line in jdl_content:
                line += u'\n'
                file.write(line)

        # create argument list file
        arguments_filename = '%s/arguments.txt' % self.job_folder

        with open(arguments_filename, 'w') as file:
            for index, line in enumerate(self.arguments):
                if index < len(self.arguments):
                    line += '\n'
                file.write(line)

        if len(self.job_folder) > 0:
            print('wrote JDL file: %s' % self.__JDLFilename)

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

        command = 'condor_submit %s' % self.__JDLFilename.split('/')[-1]
        print(command)
        try:
            subprocess.check_call(command.split())
        except subprocess.CalledProcessError as err:
            raise RuntimeError('Submit failed (RC %d)! %s' % (err.returncode, err.output))

        # jump back
        if len(main_path) > 0:
            os.chdir(main_path)

        if remove_after_start is True:
            os.remove(self.__JDLFilename)
