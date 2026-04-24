#!/usr/bin/env python3
import unittest
import os
import sys
import argparse
import subprocess
import unittest
import urllib.request


class TestChorusLapilli(unittest.TestCase):
    '''Integration testing for Chorus Lapilli

    This class handles the entire react start up, testing, and take down
    process. Feel free to modify it to suit your needs.
    '''

    # ========================== [USEFUL CONSTANTS] ===========================

    # Vite default startup address
    VITE_HOST_ADDR = 'http://localhost:5173'

    # XPATH query used to find Chorus Lapilli board tiles
    BOARD_TILE_XPATH = '//button[contains(@class, \'square\')]'

    # Sets of symbol classes - each string contains all valid characters
    # for that particular symbol
    SYMBOL_BLANK = ''
    SYMBOL_X = 'Xx'
    SYMBOL_O = '0Oo'

    # ======================== [SETUP/TEARDOWN HOOKS] =========================

    @classmethod
    def setUpClass(cls):
        '''This function runs before testing occurs.

        Bring up the web app and configure Selenium
        '''

        env = dict(os.environ)
        env.update({
            # Prevent React from starting its own browser window
            'BROWSER': 'none',
        })

        subprocess.run(['npm', 'install'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           env=env,
                           check=True)

        # Await Webserver Start
        cls.vite = subprocess.Popen(
            ['npm', 'run', 'dev'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env)

        if cls.vite.stdout is None:
            raise OSError("Vite failed to start")
        for _ in cls.vite.stdout:
            try:
                with urllib.request.urlopen(cls.VITE_HOST_ADDR):
                    break

            except IOError:
                pass

            # Ensure Vite does not terminate early
            if cls.vite.poll() is not None:
                raise OSError('Vite terminated before test')
        if cls.vite.poll() is not None:
            raise OSError('Vite terminated before test')

        cls.driver = Browser()
        cls.driver.get(cls.VITE_HOST_ADDR)
        cls.driver.implicitly_wait(0.5)

    @classmethod
    def tearDownClass(cls):
        '''This function runs after all testing have run.

        Terminate Vite and take down the Selenium webdriver.
        '''
        cls.vite.terminate()
        cls.vite.wait()
        cls.driver.quit()

    def setUp(self):
        '''This function runs before every test.

        Refresh the browser so we get a new board.
        '''
        self.driver.refresh()

    def tearDown(self):
        '''This function runs after every test.

        Not needed, but feel free to add stuff here.
        '''

    # ========================== [HELPER FUNCTIONS] ===========================

    def assertBoardEmpty(self, tiles):
        '''Checks if all board tiles are empty.

        Arguments:
          tiles: List[WebElement] - a board consisting of 9 buttons elements
        '''
        if len(tiles) != 9:
            raise AssertionError('tiles is not a 3x3 grid')
        for i, tile in enumerate(tiles):
            if tile.text.strip():
                raise AssertionError(f'tile {i} is not empty: '
                                     f'\'{tile.text}\'')

    def assertTileIs(self, tile, symbol_set):
        '''Checks if a certain tile has a certain symbol.

        Arguments:
          tile: WebElement - the button element to check
          symbol_set: str - a string containing all the valid symbols
        Raises:
          AssertionError - if tile is not in the symbol set
        '''
        if symbol_set is None:
            return
        if symbol_set == self.SYMBOL_BLANK:
            name = 'BLANK'
        elif symbol_set == self.SYMBOL_X:
            name = 'X'
        elif symbol_set == self.SYMBOL_O:
            name = 'O'
        else:
            name = 'in symbol_set'
        text = tile.text.strip()
        if ((symbol_set == self.SYMBOL_BLANK and text)
                or (symbol_set != self.SYMBOL_BLANK and not text)
                or text not in symbol_set):
            raise AssertionError(f'tile is not {name}: \'{tile.text}\'')


# =========================== [ADD YOUR TESTS HERE] ===========================

    def test_new_board_empty(self):
        '''Check if a new game always starts with an empty board.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertBoardEmpty(tiles)

    def test_button_click(self):
        '''Check if clicking the top-left button adds an X.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertTileIs(tiles[0], self.SYMBOL_BLANK)
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)

    def test_alternating_turns(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        tiles[0].click()  # X
        self.assertTileIs(tiles[0], self.SYMBOL_X)

        tiles[1].click()  # O
        self.assertTileIs(tiles[1], self.SYMBOL_O)

    def test_max_three_pieces_each(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # X placements
        tiles[0].click()  # X
        tiles[1].click()  # O
        tiles[2].click()  # X
        tiles[3].click()  # O
        tiles[4].click()  # X (X now has 3)
        tiles[5].click()  # O (O now has 3)

        # Try placing extra X (should not work)
        tiles[6].click()
        self.assertTileIs(tiles[6], self.SYMBOL_BLANK)
    def test_cannot_place_on_filled_square(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        tiles[0].click()  # X
        tiles[0].click()  # attempt overwrite

        self.assertTileIs(tiles[0], self.SYMBOL_X)
    def test_movement_phase_starts(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        tiles[0].click()  # X
        tiles[4].click()  # O
        tiles[1].click()  # X
        tiles[5].click()  # O
        tiles[3].click()  # X
        tiles[2].click()  # O

        # Now X pieces at: 0, 1, 3
        # Square 0 has adjacent empty square 4? no (O)
        # Square 1 has adjacent empty square? maybe 2 is O
        # Square 3 has adjacent empty 6 or 7? yes (6)

        tiles[3].click()  # select X
        tiles[6].click()  # move (valid)

        self.assertTileIs(tiles[3], self.SYMBOL_BLANK)
        self.assertTileIs(tiles[6], self.SYMBOL_X)

    def test_invalid_move_rejected(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # Setup movement phase
        tiles[0].click()  #X
        tiles[1].click()  #O
        tiles[2].click()  #X
        tiles[3].click()  #O
        tiles[4].click()  #X
        tiles[5].click()  #O

        # Select X
        tiles[0].click()

        # Try invalid move (non-adjacent)
        tiles[8].click()

        # Should not move
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        self.assertTileIs(tiles[8], self.SYMBOL_BLANK)

    def test_win_detection(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        tiles[0].click()  # X
        tiles[3].click()  # O
        tiles[1].click()  # X
        tiles[4].click()  # O
        tiles[2].click()  # X wins

        status = self.driver.find_element(By.CLASS_NAME, "status").text
        self.assertIn("Winner: X", status)
    
    def test_center_rule_blocks_non_winning_move(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # Setup board:
        # X will own center (4)
        tiles[4].click()  # X
        tiles[0].click()  # O
        tiles[1].click()  # X
        tiles[2].click()  # O
        tiles[3].click()  # X
        tiles[5].click()  # O

        # Board now:
        # X at 4, 1, 3
        # O at 0, 2, 5
        # Empty: 6, 7, 8

        # X owns center and tries to move NON-center piece
        tiles[3].click()  # select X at 3
        tiles[6].click()  # valid adjacent move (but NOT winning)

        # Move should be BLOCKED
        self.assertTileIs(tiles[3], self.SYMBOL_X)
        self.assertTileIs(tiles[6], self.SYMBOL_BLANK)
    
    def test_center_piece_can_move(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # Same setup
        tiles[4].click()  # X
        tiles[0].click()
        tiles[1].click()
        tiles[2].click()
        tiles[3].click()
        tiles[5].click()

        # Move CENTER piece
        tiles[4].click()  # select center
        tiles[7].click()  # valid adjacent

        # Should succeed
        self.assertTileIs(tiles[4], self.SYMBOL_BLANK)
        self.assertTileIs(tiles[7], self.SYMBOL_X)
    
    def test_center_rule_allows_winning_move(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # Setup:
        tiles[4].click()  # X (center)
        tiles[3].click()  # O
        tiles[0].click()  # X
        tiles[5].click()  # O
        tiles[2].click()  # X
        tiles[6].click()  # O

        # X at: 4, 0, 2
        # Move 4 to 1 gives:
        # 0, 1, 2 results in a WIN

        tiles[4].click()  # select center
        tiles[1].click()  # move

        self.assertTileIs(tiles[4], self.SYMBOL_BLANK)
        self.assertTileIs(tiles[1], self.SYMBOL_X)

        status = self.driver.find_element(By.CLASS_NAME, "status").text
        self.assertIn("Winner: X", status)

    def test_no_moves_after_win(self):
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)

        # Create a winning condition for X
        tiles[0].click()  # X
        tiles[3].click()  # O
        tiles[1].click()  # X
        tiles[4].click()  # O
        tiles[2].click()  # X -> X wins

        # Verify win occurred
        status = self.driver.find_element(By.CLASS_NAME, "status").text
        self.assertIn("Winner: X", status)

        # Try to make another move
        tiles[5].click()

        # Board should NOT change
        self.assertTileIs(tiles[5], self.SYMBOL_BLANK)

        # Also verify original winning tiles are unchanged
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        self.assertTileIs(tiles[1], self.SYMBOL_X)
        self.assertTileIs(tiles[2], self.SYMBOL_X)

# ================= [DO NOT MAKE ANY CHANGES BELOW THIS LINE] =================

if __name__ != '__main__':
    from selenium.webdriver import Firefox as Browser
    from selenium.webdriver.common.by import By
else:
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='Chorus Lapilli Tester')
    parser.add_argument('-b',
                        '--browser',
                        action='store',
                        metavar='name',
                        choices=['firefox', 'chrome', 'safari'],
                        default='firefox',
                        help='the browser to run tests with')
    parser.add_argument('-c',
                        '--change-dir',
                        action='store',
                        metavar='dir',
                        default=None,
                        help=('change the working directory before running '
                              'tests'))

    # Change the working directory
    options = parser.parse_args(sys.argv[1:])
    # Import different browser drivers based on user selection
    try:
        if options.browser == 'firefox':
            from selenium.webdriver import Firefox as Browser
        elif options.browser == 'chrome':
            from selenium.webdriver import Chrome as Browser
        else:
            from selenium.webdriver import Safari as Browser
        from selenium.webdriver.common.by import By
    except ImportError as err:
        print('[Error]',
              err, '\n\n'
              'Please refer to the Selenium documentation on installing the '
              'webdriver:\n'
              'https://www.selenium.dev/documentation/webdriver/'
              'getting_started/',
              file=sys.stderr)
        sys.exit(1)

    if options.change_dir:
        try:
            os.chdir(options.change_dir)
        except OSError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

    if not os.path.isfile('package.json'):
        print('Invalid directory: cannot find \'package.json\'',
              file=sys.stderr)
        sys.exit(1)

    tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestChorusLapilli)
    unittest.TextTestRunner().run(tests)
