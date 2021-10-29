import time
import traceback

import beepy as beep
import clipboard

from utils import get_repo_path


class ClipboardMonitor:
    HEADER = ['target_word', 'context', 'delay_since_prev_word', 'timestamp']

    def __init__(self):
        self.previous = clipboard.paste()

    @staticmethod
    def _store(word):
        with open(f'{get_repo_path()}/data/clipboard.csv', 'a') as f:
            f.write(word + '\n')
            print(word)

    def _check_once(self):
        value = clipboard.paste()
        if value == self.previous:
            return
        self.previous = value
        value = value.strip()
        if len(value) > 200:
            print(f'   value is too long: {value[100]}...')
            return
        elif '\n' in value:
            print(f'   value has newline character, skipping')
            return
        # value = value.split()
        # target_value = value[0]
        # if not target_value.isalpha():
        #     print(f'   bad value: {value}')
        #     return
        self._store(value)
        # pronounce(target_value)
        beep.beep(2)

    def serve(self):
        while True:
            try:
                self._check_once()
            except Exception:
                traceback.print_exc()
            time.sleep(1)


if __name__ == '__main__':
    ClipboardMonitor().serve()
