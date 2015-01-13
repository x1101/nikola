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
        if len(levels) == 0: return []
        level = levels[0]
        tasks = generate_tasks('level_' + str(level), self.program.get_tasks(level))
        if len(levels) > 1:
            eol_name = 'level_' + str(level) + '_wait'
            tasks.extend(generate_tasks(eol_name, { 'basename': eol_name, 'task_dep': [ t.name for t in tasks ], 'actions': [ ] }))
            next_level = levels[1]
            tasks.append(Task('level_' + str(next_level) + '_generate', None, loader=DelayedLoader(lambda: self._generate_more(levels[1:]), executed='level_' + str(level) + '_wait')))
        return tasks

    def _generate_more(self, levels):
        tasks = self._generate_level(levels)
        for t in tasks:
            yield t

    def load_tasks(self, cmd, opt_values, pos_args):
        DOIT_CONFIG = {
            'reporter': ExecutedOnlyReporter,
            'outfile': sys.stderr,
        }
        tasks = self._generate_level(self.program.get_task_levels())
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
        return [1, 2, 3]

    def _create_tasks(self, *files):
        for src_file, dst_file in files:
            yield {
                'basename': 'copy',
                'name': dst_file,
                'file_dep': [src_file],
                'targets': [dst_file],
                'actions': [(self._do_copy, (src_file, dst_file))],
            }

    def _get_tasks_impl(self, level):
        if level == 1:
            yield self._create_tasks(('1', 'dest/1.a'), ('2', 'dest/2.a'), ('dest/2.a', 'dest/2.b'))
        elif level == 2:
            yield self._create_tasks(('dest/1.a', 'dest/1.b'))
        elif level == 3:
            yield self._create_tasks(('1', 'dest/1.c'), ('dest/2.b', 'dest/2.c'))

    def get_tasks(self, level):
        yield {
            'basename': 'copy',
            'name': None,
            'doc': 'Copies modified or non-existing files over',
        }
        yield self._get_tasks_impl(level)

    def get_all_tasks(self):
        yield {
            'basename': 'copy',
            'name': None,
            'doc': 'Copies modified or non-existing files over',
        }
        for level in self.get_task_levels():
            yield self._get_tasks_impl(level)


def main(args=None):
    program = Program()
    return MyDoit(program).run(args)


if __name__ == "__main__":
    try:
        shutil.rmtree('dest', True)
    except:
        pass
    os.mkdir('dest')
    write_content('1', 'bla')
    write_content('2', 'bla')
    sys.exit(main(['run', '-n', '4', '-P', 'thread']))
