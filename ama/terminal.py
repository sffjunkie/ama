# Copyright 2009-2013, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    import readline
except ImportError:
    pass

try:
    # Try assigning the Python 2 version of the input function
    input = raw_input
except:
    pass

from os.path import normpath
from collections import OrderedDict

from ama import Asker
from ama.validator import validate_bool
from ama.color import bright_green, cyan, bright_red

class TerminalAsker(Asker):
    """Ask the questions by using the terminal"""
    
    def __init__(self, title, preamble='', filename=''):
        Asker.__init__(self, filename)
        self._title = title
        self._preamble = preamble
        self._ask = OrderedDict()
    
    def add_question(self, key, question):
        """Add a question to the list of questions.
        
        Called by the :meth:`Asker.ask` method or by your code.
        """
        
        self._ask[key] = question
    
    def go(self, initial_answers):
        """Perform the question asking"""
        
        print(bright_green(self._title))
        print(bright_green('-'*len(self._title)))
        if self._preamble != '':
            print('\n%s' % self._preamble)
        print('\n')
           
        result = {}
        try:
            answers = {}
            for key, question in self._ask.items():
                answer = self._ask_question(question, initial_answers, answers)
                answers[key] = answer
                
            result[u'answers'] = answers
            result[u'valid'] = True
            result[u'result'] = 'ok'
        except (KeyboardInterrupt, EOFError):
            try:
                result[u'result'] = 'cancel'
                print('\n[Interrupted]\n')
            except:
                pass
            
        return result

    def _ask_question(self, question, initial_answers, answers):
        """Ask a single question"""
        
        prompt_tail = ''
        if question.validator == 'yesno':
            if not question.label.endswith(' (y/n)'):
                prompt_tail = ' (y/n)'
            if question.default == True or question.default == 'y':
                prompt_tail += ' [y]'
            elif question.default == False or question.default == 'n':
                prompt_tail += ' [n]'
            default = validate_bool(question.default)
        else:
            try:
                default = question.default.format(**answers)
            except:
                default = question.default
            
            if question.validator and question.validator.startswith('path'):
                default = normpath(default)
            
            prompt_tail = ' [%s]' % default
        
        prompt = '%s%s: ' % (question.label, prompt_tail)
            
        while True:
            answer = input(cyan(prompt))
            stripped = answer.strip()
            if stripped == '?':
                print(question.help_text)
                continue
            
            if stripped == '':
                answer = default
                
            try:
                validate = self.validator(question.type, question.validator)
                answer = validate(answer)
            except Exception as err:
                print(bright_red('* %s\n' % str(err)))
                print(question.help_text)
                continue
            break
    
        return answer
