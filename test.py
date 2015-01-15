#!/usr/bin/python3
from __future__ import print_function, unicode_literals
import copy
import os
import shutil
import sys

from doit.loader import generate_tasks
from doit.task import Task, DelayedLoader
from doit.cmd_base import TaskLoader
from doit.reporter import ExecutedOnlyReporter
from doit.doit_cmd import DoitMain


class MyTaskLoader(TaskLoader):
    def __init__(self, program):
        self.program = program

    def _generate_level(self, levels):
        level = levels[0]
        names = set()

        def flatten(task):
            if isinstance(task, dict):
                yield task
            else:
                for t in task:
                    for ft in flatten(t):
                        yield ft

        for task in self.program.get_tasks(level):
            for t in flatten(task):
                names.add(t['basename'])
                yield t
        mid_name = 'level_' + str(level) + '_wait'
        done_name = 'level_' + str(level) + '_done'
        yield { 'basename': mid_name, 'doc': None, 'name': None, 'task_dep': list(names) }
        done_deps = [mid_name]
        if len(levels) > 1:
            gen_name = 'level_' + str(levels[1]) + '_done'
            done_deps.append(gen_name)
            yield Task(gen_name, None, loader=DelayedLoader(lambda: self._generate_level(levels[1:]), executed=mid_name))
        yield { 'basename': done_name, 'doc': None, 'name': None, 'task_dep': done_deps }

    def _generate_all(self, levels):
        names = set()
        for level in levels:
            for task in self.program.get_tasks(level):
                yield task
        #yield { 'basename': 'level_all_done', 'doc': None, 'name': None, 'task_dep': [] }

    def load_tasks(self, cmd, opt_values, pos_args):
        DOIT_CONFIG = {
            'reporter': ExecutedOnlyReporter,
            'outfile': sys.stderr,
        }
        levels = self.program.get_task_levels()
        if cmd.execute_tasks:
            tasks = generate_tasks('level_' + str(levels[0]) + '_done', self._generate_level(levels))
        else:
            tasks = generate_tasks('level_all_done', self._generate_all(levels))
        return tasks, DOIT_CONFIG


class MyDoit(DoitMain):
    def __init__(self, program):
        self.program = program
        self.TASK_LOADER = MyTaskLoader
        self.task_loader = self.TASK_LOADER(program)


def get_content(filename):
    with open(filename, "rb") as f:
        return f.read().decode('utf-8')


def write_content(filename, content):
    with open(filename, "wb") as f:
        f.write(content.encode('utf-8'))


class Program():
    def _do_copy(self, source, destination):
        content = get_content(source)
        if not content.startswith('copy'):
            content = ''
        content += 'copy "{0}" to "{1}"\n'.format(source, destination)
        write_content(destination, content)

    def get_task_levels(self):
        return [1, 2, 3, 4]

    def _create_tasks(self, basename, *files):
        for src_file, dst_file in files:
            yield {
                'basename': basename,
                'name': dst_file,
                'file_dep': [src_file],
                'targets': [dst_file],
                'actions': [(self._do_copy, (src_file, dst_file))],
                'clean': True,
            }

    def _get_tasks_impl(self, suffix, level):
        if level == 1:
            yield self._create_tasks('copy' + suffix, ('1', 'dest/1.a'), ('2', 'dest/2.a'), ('dest/2.a', 'dest/2.b'))
        elif level == 2:
            yield self._create_tasks('copy' + suffix, ('dest/1.a', 'dest/1.b'), ('2', 'dest/2.e'))
        elif level == 3:
            yield self._create_tasks('copy' + suffix, ('1', 'dest/1.c'), ('dest/2.b', 'dest/2.c'))
        elif level == 4:
            yield self._create_tasks('copy' + suffix, ('dest/1.c', 'dest/1.d'), ('dest/2.d', 'dest/2.f'), ('dest/2.c', 'dest/2.d'))

    def get_tasks(self, level):
        suffix = '_' + str(level)
        yield {
            'basename': 'copy' + suffix,
            'name': None,
            'doc': 'Copies modified or non-existing files over',
        }
        yield self._get_tasks_impl(suffix, level)


def main(args=None):
    program = Program()
    return MyDoit(program).run(args)


if __name__ == "__main__":
    #sys.exit(main(['clean']))
    try:
        pass
        shutil.rmtree('dest', True)
    except:
        pass
    os.mkdir('dest')
    write_content('1', 'bla')
    write_content('2', 'bla')
    sys.exit(main(['list', '--all']))
    #sys.exit(main(['run', '-v', '2']))
    #sys.exit(main(['run', '-n', '4', '-v', '2', '-P', 'thread']))
