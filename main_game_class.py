# Raz's Project 2017/2018
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from random import randrange
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.uix.layout import Layout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.animation import Animation
from kivy.graphics.texture import Texture
from kivy.utils import escape_markup
import time
import copy

from itertools import permutations
import itertools
import math
from kivy.core.window import Window
from kivy.clock import Clock
from functools import partial

# TODO(!): Finish INSTRUCTIONS and then -> ANIMATION ! !
# TODO(2): Ask the user about the colors of the players. Give option to RANDOM -> Run all the colors in 3 squars some minutes... :-)


"""
Important Concepts:
    Country:
        - Side Country -> Relative expression. Means to two countries that are adjacent to each other, "Neighbor Countries".
        - Bloc -> List of countries that are adjacent to each other and have a common control.
        - Ext Country -> A country in a bloc which has a side country with a different control.

    Game:
        - Mode -> shortcut for describe the current game's situation for the user:
                    'cc' - for Choose Country -> The user need to choose a country belongs to him.
                    'csc' - for Choose Side Country -> the user need to choose a country
                                                        which is a side country for the first country he has chose.
                    'aa' - for Add Armies -> (At the beginning of the user turn) The user need to add armies to his countries.
                    'ct' - for Computer Turn -> Now it is the computer turn, not really used...
                    'pa' - for Pass Armies -> The user had already chose 2 countries (the first one must be one of his countries)
                                                and now hw need to pass armies from the first one to the other.

    Computer Turn:
        - Easy Kill / Easy Killing -> When the computer can attack a user's bloc contains only one country.

    *Note: Those concepts are displayed with asterisk(*) or by CAPITAL LETTERS.
"""


class ImageButton(ButtonBehavior, Image):
    # Image which is click-able. Used for icons...
    def __init__(self, source, click_fun, pos, size, **kwargs):
        """
        Create an ImageButton object.

        :param source: Image source. --> str
        :param click_fun: Called when the object is pressed. --> function
        :param pos: Object's position on the board.  --> Tuple(width, hieght)
        :param size: Object's size on the board.
        """
        ButtonBehavior.__init__(self)
        Image.__init__(self)

        self.source = source
        if click_fun:
            self.bind(on_press=click_fun)
        self.pos = pos
        self.size = size


class ButtonCountry(ButtonBehavior, Image):
    # Visual country on the map.
    def __init__(self, control, **kwargs):
        """
        Creates a ButtonCountry object.
        :param control: Country's control. can be only:
                            0 - neutral.
                            1 - computer.
                            2 - user.
        """
        ButtonBehavior.__init__(self)
        Image.__init__(self)

        # Set Background Color
        if control == 0:
            self.source = 'green.png'
        elif control == 1:
            self.source = 'red.png'
        elif control == 2:
            self.source = 'blue.png'
        else:
            print "Error: The control is no 0 or 1 or 2 !"

        self.control = control

    # Temporary
    # Prints click's position.
    '''def on_touch_down(self, touch):

        print "{}, {}".format(int(touch.x), int(touch.y))
        #  self.pos = (touch.x, touch.y)'''
    ######################################################


class Country(Layout):
    # The sign which marks the CHOSE_COUNTRY on the map.
    SIGN = Label(text='^', color=(1, 0, 0, 1), markup=True, size=(50, 50), font_size=30)

    # The country which is chosen by the user.
    CHOSE_COUNTRY = None

    # The country user want to pass armies from CHOSE_COUNTRY
    TARGET_COUNTRY = None

    # The countries that the user conquered in the last turn
    OCCUPIED_COUNTRIES = []

    def __init__(self, control, side_countries, continent, pos, armies_counter=0, is_tot=False, **kwargs):
        """
        :param control: int, can be only:
            0 for neutral
            1 for computer's control
            2 for user's control
        :param side_countries: list of Countries
        :param continent: int - can be only:
            1 for Africa
            2 for Asia
            3 for Europe
            4 for Australia
            5 for America
            * Note: This attr is not used right now.
        :param pos: Tuple(x, y) - The button position.
        :param is_tot: If this is a toturial country.
        """
        Layout.__init__(self, **kwargs)

        # Layout attributes
        self.size = (0, 0)
        # self.size_hint = (3, 3)  TODO: Maybe not important

        # Country attributes
        self.control = control
        if armies_counter:
            if control != 2:
                self.armies_counter = -abs(armies_counter)
            else:
                self.armies_counter = abs(armies_counter)

        else:
            # Decide the armies_counter according the country's control.
            # Ease the initiate and changing the map at the beginning of the game.
            if control == 0:
                self.armies_counter = 2  # randrange(0, 6)
            elif self.control == 2:
                self.armies_counter = 5
            else:
                self.armies_counter = 5

            if self.control != 2:  # Not user country
                self.armies_counter *= -1

        self.side_countries = side_countries
        self.continent = continent  # Unused right now

        # Button Attributes:
        self.button_pos = pos
        self.button_size = (15, 15)
        self.button_is_big = False

        # Text - Number of Armies
        self.armies_counter_label = Label(text=str(abs(self.armies_counter)), markup=True,
                                          size=(15, 15), pos=(self.button_pos[0], self.button_pos[1] + 15))
        self.armies_counter_label.color = (0, 10, 1, 1)

        self.add_widget(self.armies_counter_label)

        # Add btn to the map
        self.btn = ButtonCountry(control=self.control)
        self.btn.bind(on_press=self.country_click)
        self.btn.pos = self.button_pos
        self.btn.size = self.button_size
        self.add_widget(self.btn)

        self.is_tot = is_tot

        # GridLayout - showed after the user choose CHOSE_COUNTRY and TARGET_COUNTRY
        self.armies_to_pass = None

    def _keyboard_closed(self):
        # Calls when the keyboard closed.
        print '_keyboard_closed'
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Called when the user click on the keyboard.

        if keycode[0] == 13 or keycode[0] == 271:  # Enter
            pass

        if keycode[0] == 32:  # Space
            # Closes the last country that opened.

            if Country.TARGET_COUNTRY is not None:
                Country.TARGET_COUNTRY.country_click(555)
                print 'Close TARGET_COUNTRY'
                return

            elif Country.CHOSE_COUNTRY is not None:
                Country.CHOSE_COUNTRY.country_click(554)
                print 'Close CHOSE_COUNTRY'
                return

        if self.armies_to_pass:
            # Choose how many armies to pass --> keycode[0] need to be a number.

            num = keycode[0] - 48
            if 208 < num < 218:
                num -= 208
            print 'num = ', num
            print 'self.armies_to_pass.cols = ', self.armies_to_pass.cols
            if 0 < num < self.armies_to_pass.cols:
                if self.armies_to_pass is not None:
                    b = Button(text=str(num))
                    self.choose_armies_number(b)

    def refresh_armies_counter(self, armies):
        """
        Refreshes the country's armies number, logical and visual.

        :param armies: The new number of armies
        :return: None
        """
        self.armies_counter = armies
        self.armies_counter_label.text = str(abs(armies))

    def add_armies_to_country(self, armies_to_add):
        """
        Adds to the country (armies_to_add) armies.
        Positive\Negative according the control

        :param armies_to_add: Natural Int!! How many armies to add?
        :return: None
        """

        armies_to_add = abs(armies_to_add)  # Input Check
        if self.control == 2:
            self.refresh_armies_counter(armies=self.armies_counter + armies_to_add)
        else:
            self.refresh_armies_counter(armies=self.armies_counter - armies_to_add)

    def sub_armies_to_country(self, armies_to_sub):
        """
        Reduces the country (armies_to_add) armies.
        Positive\Negative according the control.

        :param armies_to_sub: Natural Int!! How many armies to decrease?
        :return: None
        """

        armies_to_sub = abs(armies_to_sub)  # Input Check
        if self.control == 2:
            self.refresh_armies_counter(armies=self.armies_counter - armies_to_sub)
        else:
            self.refresh_armies_counter(armies=self.armies_counter + armies_to_sub)

    def change_button_size_on_the_layout(self, to_big):
        """
        This method changes the btn size.
        It called when the user click on the country or leave it.

        :param (bool) to_big: True - change to big
                        False - Change to Small
        :return: None
        """

        if (to_big and self.button_is_big) or (not to_big and not self.button_is_big):
            # No change needed
            return

        # Changes the button size (and a little bit moves it):

        # New Button
        temp = ButtonCountry(control=self.control)
        temp.source = self.btn.source
        temp.bind(on_press=self.country_click)

        if self.button_is_big:
            # Decrease the size and change the pos
            temp.size = self.button_size
            temp.pos = self.button_pos
            self.button_is_big = False
        else:
            # Increase the pos and the size
            temp.pos = (self.btn.pos[0] - 10, self.btn.pos[1] - 10)
            temp.size = (28, 28)
            self.button_is_big = True

        # Remove the old button from the layout
        self.remove_widget(self.btn)
        self.btn = temp

        # Add the new button to the layout
        self.add_widget(self.btn)

    @staticmethod
    def close_chose_country_and_so_on():
        """
        This static method -    Closes the TARGET_COUNTRY (if there is) and its gridLayout.
                                Closes the CHOSE_COUNTRY.
                                Changes the colors of the side_countries.

        :return: None
        """
        if Country.CHOSE_COUNTRY:
            if Country.TARGET_COUNTRY:
                Country.TARGET_COUNTRY.change_button_size_on_the_layout(to_big=False)
                Country.TARGET_COUNTRY.remove_widget(Country.TARGET_COUNTRY.armies_to_pass)
                Country.TARGET_COUNTRY = None

            for side_country in Country.CHOSE_COUNTRY.side_countries:
                if side_country.control == 0:
                    side_country.btn.source = 'green.png'
                elif side_country.control == 1:
                    side_country.btn.source = 'red.png'
                elif side_country.control == 2:
                    side_country.btn.source = 'blue.png'
            Country.CHOSE_COUNTRY.change_button_size_on_the_layout(to_big=False)
            Country.CHOSE_COUNTRY.remove_widget(Country.SIGN)
            Country.CHOSE_COUNTRY = None

    def make_chose_country_and_so_on(self):
        """
        Makes self to be the CHOSE_COUNTRY:
                Makes it big.
                Adds a Sign.
                Changes its side_countries's colors.

        :return: None
        """

        if not Country.CHOSE_COUNTRY and not Country.TARGET_COUNTRY and self.control == 2:
            # Change the side countries source to be targets.
            for side_country in self.side_countries:
                if side_country.btn.control == 1:
                    side_country.btn.source = 'x_red.png'
                elif side_country.btn.control == 0:
                    side_country.btn.source = 'x_green.png'
                elif side_country.btn.control == 2:
                    side_country.btn.source = 'arrow_blue.png'

            self.change_button_size_on_the_layout(True)

            Country.CHOSE_COUNTRY = self
            Country.SIGN.pos = (self.button_pos[0] - 20, self.button_pos[1] - 40)
            self.add_widget(Country.SIGN)  # Mark this country.

    def country_click(self, touch):
        """
        Handle all the countries clicks: user's, computer's or neutral.
        IF all the Countries are small and now it is the user turn and he click on one of his countries -
            this is the the CHOSE_COUNTRY which can pass armies from it to its side countries.
        ELSE IF the country is a CHOSE_COUNTRY.side_country -
            the user can pass armies from CHOSE_COUNTRY to this country (self).
        ELSE IF the country belongs to the user - it changes the CHOSE_COUNTRY.
        ELSE - The user cannot click on this country.

        :param touch: ButtonCountry object.
        :return None
        """

        if self.is_tot:
            if Game.MODE == 'aa':
                if Game.ARMIES_LABEL_TRY.text != '0':
                    Game.ARMIES_LABEL_TRY.text = str(int(Game.ARMIES_LABEL_TRY.text) - 1)
                    self.add_armies_to_country(1)
                else:
                    change_mode('cc')
            elif Game.MODE == 'cc':

                if self.btn.control == 2:
                    # Create new CHOSE_COUNTRY
                    self.make_chose_country_and_so_on()
                    change_mode('csc')
                    return

            elif Game.MODE == 'csc':  # A country was chosen
                if self is Country.CHOSE_COUNTRY:  # This country is the user's chosen country

                    Country.close_chose_country_and_so_on()
                    change_mode('cc')
                    return

                else:  # There is a CHOSE_COUNTRY but it's not this country
                    if self in Country.CHOSE_COUNTRY.side_countries:  # A side country

                        if not Country.CHOSE_COUNTRY.armies_counter:
                            print 'No armies to pass'
                            return

                        else:
                            self.change_button_size_on_the_layout(True)
                            Country.TARGET_COUNTRY = self
                            self.armies_gridlayout_changer()
                            change_mode('pa')
                            return

                    elif self.control == 2:  # New CHOSE_COUNTRY
                        Country.close_chose_country_and_so_on()
                        self.make_chose_country_and_so_on()
                        return
            elif Game.MODE == 'pa':
                if self is Country.CHOSE_COUNTRY:
                    Country.close_chose_country_and_so_on()
                    change_mode('cc')
                elif self is Country.TARGET_COUNTRY:
                    self.change_button_size_on_the_layout(False)
                    if self.armies_to_pass and self.armies_to_pass.parent:
                        self.remove_widget(self.armies_to_pass)
                    Country.TARGET_COUNTRY = None

                    change_mode('csc')
                    return

                elif self not in Country.CHOSE_COUNTRY.side_countries and self.control == 2:
                    Country.close_chose_country_and_so_on()
                    self.make_chose_country_and_so_on()
                    change_mode('csc')
                    return

            return

        print self.button_pos

        if self.control != 2:
            if not Country.CHOSE_COUNTRY:
                Game.NOT_USER_COUNTRY_LABEL.text = add_enter_in_instruction(Game.RES_DICT['warn_not_user_country'])
                return
            if self not in Country.CHOSE_COUNTRY.side_countries:
                Game.NOT_USER_COUNTRY_LABEL.text = add_enter_in_instruction(Game.RES_DICT['warn_not_user_country'])
                return
        if self in Country.OCCUPIED_COUNTRIES:
            if not Country.CHOSE_COUNTRY:
                Game.NOT_USER_COUNTRY_LABEL.text = add_enter_in_instruction(Game.RES_DICT['warn_not_user_country_yet'])
                return
            if self not in Country.CHOSE_COUNTRY.side_countries:
                Game.NOT_USER_COUNTRY_LABEL.text = add_enter_in_instruction(Game.RES_DICT['warn_not_user_country_yet'])
                return

        Game.NO_ARMIES_IN_CHOSE_COUNTRY_LABEL.text = ''
        Game.NOT_USER_COUNTRY_LABEL.text = ''
        Game.NOT_USER_COUNTRY_LABEL.text = ''

        if Game.MODE == 'cc':  # User's turn - (cc = Choose Country)

            if self in Country.OCCUPIED_COUNTRIES:
                # User cannot click on this country in this turn. Only in the next turn.
                print "Not user's country YET"
                Game.NOT_USER_COUNTRY_LABEL.text = add_enter_in_instruction(Game.RES_DICT['warn_not_user_country_yet'])
                return
            else:
                Game.NOT_USER_COUNTRY_LABEL.text = ""

            if self.btn.control == 2:
                # Create new CHOSE_COUNTRY
                self.make_chose_country_and_so_on()
                change_mode('csc')
                return

            else:
                Game.NOT_USER_COUNTRY_LABEL.text = Game.NOT_USER_COUNTRY_TEXT

        elif Game.MODE == 'pa':
            if self is Country.CHOSE_COUNTRY:
                Country.close_chose_country_and_so_on()
                change_mode('cc')
            elif self is Country.TARGET_COUNTRY:
                self.change_button_size_on_the_layout(False)
                if self.armies_to_pass and self.armies_to_pass.parent:
                    self.remove_widget(self.armies_to_pass)
                Country.TARGET_COUNTRY = None

                change_mode('csc')
                return

            elif self not in Country.CHOSE_COUNTRY.side_countries and self.control == 2:
                Country.close_chose_country_and_so_on()
                self.make_chose_country_and_so_on()
                change_mode('csc')
                return

        elif Game.MODE == 'csc':  # A country was chosen
            if self is Country.CHOSE_COUNTRY:  # This country is the user's chosen country

                Country.close_chose_country_and_so_on()
                change_mode('cc')
                return

            else:  # There is a CHOSE_COUNTRY but it's not this country
                if self in Country.CHOSE_COUNTRY.side_countries:  # A side country

                    if not Country.CHOSE_COUNTRY.armies_counter:
                        print 'No armies to pass'
                        Game.NOT_USER_COUNTRY_LABEL.text = add_enter_in_instruction(Game.RES_DICT['warn_no_armies_in_chose_country'])
                        return

                    else:
                        self.change_button_size_on_the_layout(True)
                        Country.TARGET_COUNTRY = self
                        self.armies_gridlayout_changer()
                        change_mode('pa')
                        return

                elif self.control == 2:  # New CHOSE_COUNTRY
                    Country.close_chose_country_and_so_on()
                    self.make_chose_country_and_so_on()
                    return

        elif Game.MODE == 'aa':
            if self.control == 2:

                self.refresh_armies_counter(self.armies_counter + 1)
                Game.refresh_addition_armies_label(Game.ADDITION_ARMIES - 1)
            else:
                Game.NOT_USER_COUNTRY_LABEL.text = Game.RES_DICT['warn_not_user_country']

    def armies_gridlayout_changer(self):
        """
        Changes a CHOSE_COUNTRY's side_country options to pass armies:
                IF the side_country has this table --> Clear it and shows an updated table.
                ELSE --> create a new table.

        :return None
        """
        if self.armies_to_pass:
            self.remove_widget(self.armies_to_pass)
        if Country.CHOSE_COUNTRY.armies_counter == 0:
            # No table needed
            return

        change_mode('pa')
        self.armies_to_pass = GridLayout(cols=Country.CHOSE_COUNTRY.armies_counter + 1,
                                         size=(23 * Country.CHOSE_COUNTRY.armies_counter, 20),
                                         pos=(self.button_pos[0] + 20, self.button_pos[1]))

        # Insert values to the table:
        for num in xrange(1, Country.CHOSE_COUNTRY.armies_counter + 1):
            num_button = Button(text=str(num))
            num_button.bind(on_press=self.choose_armies_number)

            self.armies_to_pass.add_widget(num_button)

        # Show the table.
        self.add_widget(self.armies_to_pass)

        if self.armies_to_pass:
            # Options to choose how many armies to pass by the keyboard.
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def change_control(self, new_control):
        """
        Changes self.control logical, visual and updates the armies_counter (Negative/Positive)

        :param new_control: The new control of self.
        :return: None
        """
        if self.control != new_control:
            if 0 <= new_control <= 2:
                self.control = new_control
                self.btn.control = new_control
                if new_control == 0:
                    self.armies_counter = -abs(self.armies_counter)
                    self.btn.source = 'green.png'
                elif new_control == 1:
                    self.btn.source = 'red.png'
                    self.armies_counter = -abs(self.armies_counter)
                elif new_control == 2:
                    self.btn.source = 'blue.png'
                    self.armies_counter = abs(self.armies_counter)
            else:
                print 'Input Error in method: change_control'
        else:
            print 'change_control -> No Change Needed'

    def choose_armies_number(self, button):
        """
        Handle the clicks on a buttons in the armeis_to_pass gridLayout.

        :param button: The button in the gridLayout, symbol to the number of armies the user wants to pass.
        :return: None
        """

        if Country.CHOSE_COUNTRY is None or Country.TARGET_COUNTRY is None:
            return
        if Country.CHOSE_COUNTRY.armies_counter > 0:
            pass_armies = int(button.text)
            Country.CHOSE_COUNTRY.armies_counter -= pass_armies
            self.armies_counter += pass_armies
            prev_control = self.control
            if self.armies_counter > 0:
                self.control = 2
                self.btn.source = "blue.png"
                if prev_control != 2:
                    # User conquered a country !
                    Country.OCCUPIED_COUNTRIES.append(self)

            Country.CHOSE_COUNTRY.armies_counter_label.text = str(abs(Country.CHOSE_COUNTRY.armies_counter))
            self.armies_counter_label.text = str(abs(self.armies_counter))
            self.armies_gridlayout_changer()

        if Country.CHOSE_COUNTRY.armies_counter == 0:
            # Close immediately the CHOSE_COUNTRY because it doesn't have armies to pass anymore.
            Country.TARGET_COUNTRY.country_click(553)
            Country.CHOSE_COUNTRY.country_click(552)


def ext_country(country):
    """
    *Helping function to 'ext_countries_in_bloc'.

    :param country: Country in bloc.
    :return: whether the country has a side country with a different control.
    """
    for side_country in country.side_countries:
        if side_country.control != country.control:
            return True
    return False


def ext_countries_in_bloc(bloc):
    """

    :param bloc: *Bloc
    :return: All the ext-countries* in the bloc.
    """
    the_ext_countries = list()
    for country in bloc:
        if ext_country(country):
            the_ext_countries.append(country)
    return the_ext_countries


def sum_armies_in_bloc(bloc):
    """

    :param bloc: *Bloc
    :return: The sum of the armies in the bloc. NOT ABS !
    """
    sum_armies = 0
    for country in bloc:
        sum_armies += country.armies_counter
    return sum_armies


def bloc_equal_bloc(bloc1, bloc2):
    """

    :param bloc1: *Bloc
    :param bloc2: *Bloc
    :return: whether the blocs equals - have the same countries.
    """
    for country1 in bloc1:
        if country1 not in bloc2:
            return False
    return True


def common_countries_between_blocs(bloc1, bloc2):
    """

    :param bloc1: *Bloc
    :param bloc2: *Bloc
    :return: List contains all the commons countries in the two blocs.
    """
    commons = list()
    for country1 in bloc1:
        if country1 in bloc2:
            commons.append(country1)
    return commons


# TODO: Unused Function
'''
def copy_all_blocs(all_blocs):
    the_copy = list()
    for bloc in all_blocs:
        bloc_copy = list()
        for country in bloc:
            bloc_copy.append(Country(country.control, country.side_countries, country.continent, country.pos,
                                     armies_counter=country.armies_counter))
        the_copy.append(bloc_copy)
    return the_copy
'''


def create_start_countries_dict():
    """
    This function returns a dictionary contains all the countries in the game.
        keys -> name.
        values -> Country object.
    :return: countries_dic --> Dictionary
    """
    countries_dic = dict()
    countries_dic['egypt'] = Country(0, set([]), 1, (620, 495))
    countries_dic['usa_east'] = Country(0, set([]), 5, (245, 610))
    countries_dic['usa_west'] = Country(0, set([]), 5, (124, 623))
    countries_dic['canada'] = Country(1, set([]), 5, (228, 770))
    countries_dic['australia'] = Country(2, set([]), 1, (993, 168))
    countries_dic['russia_east'] = Country(1, set([]), 2, (689, 708))
    countries_dic['russia_west'] = Country(0, set([]), 2, (916, 777))
    countries_dic['france'] = Country(0, set([]), 3, (540, 640))
    countries_dic['spain'] = Country(0, set([]), 3, (514, 596))
    countries_dic['india'] = Country(0, set([]), 2, (799, 481))
    countries_dic['middle_east_israel'] = Country(0, set([]), 2, (655, 543))
    countries_dic['iran'] = Country(0, set([]), 2, (710, 550))
    countries_dic['europe_east'] = Country(0, set([]), 2, (614, 679))
    countries_dic['china'] = Country(0, set([]), 2, (868, 583))
    countries_dic['mongolia'] = Country(0, set([]), 2, (860, 640))
    countries_dic['kazakhstan'] = Country(0, set([]), 2, (750, 650))
    countries_dic['mexico'] = Country(0, set([]), 2, (151, 520))
    countries_dic['south_america_n'] = Country(0, set([]), 2, (242, 384))
    countries_dic['south_america_s'] = Country(2, set([]), 2, (304, 103))
    countries_dic['brazil'] = Country(0, set([]), 2, (321, 281))
    countries_dic['denmark'] = Country(0, set([]), 2, (613, 779))
    countries_dic['algeria'] = Country(0, set([]), 2, (536, 509))
    countries_dic['congo'] = Country(0, set([]), 2, (602, 330))
    countries_dic['madagascar'] = Country(0, set([]), 2, (690, 228))
    countries_dic['south_africa'] = Country(0, set([]), 2, (605, 213))
    countries_dic['greenland'] = Country(0, set([]), 2, (487, 846))
    countries_dic['chad'] = Country(0, set([]), 2, (585, 436))
    countries_dic['indonesia'] = Country(0, set([]), 2, (937, 342))

    countries_dic['usa_east'].side_countries.add(countries_dic['usa_west'])
    countries_dic['usa_west'].side_countries.add(countries_dic['usa_east'])
    countries_dic['canada'].side_countries.add(countries_dic['greenland'])
    countries_dic['greenland'].side_countries.add(countries_dic['canada'])
    countries_dic['mexico'].side_countries.add(countries_dic['usa_east'])
    countries_dic['usa_east'].side_countries.add(countries_dic['mexico'])
    countries_dic['mexico'].side_countries.add(countries_dic['usa_west'])
    countries_dic['usa_west'].side_countries.add(countries_dic['mexico'])
    countries_dic['canada'].side_countries.add(countries_dic['usa_east'])
    countries_dic['usa_east'].side_countries.add(countries_dic['canada'])
    countries_dic['canada'].side_countries.add(countries_dic['usa_west'])
    countries_dic['usa_west'].side_countries.add(countries_dic['canada'])
    countries_dic['egypt'].side_countries.add(countries_dic['middle_east_israel'])
    countries_dic['middle_east_israel'].side_countries.add(countries_dic['egypt'])
    countries_dic['india'].side_countries.add(countries_dic['china'])
    countries_dic['china'].side_countries.add(countries_dic['india'])
    countries_dic['greenland'].side_countries.add(countries_dic['denmark'])
    countries_dic['denmark'].side_countries.add(countries_dic['greenland'])
    countries_dic['russia_east'].side_countries.add(countries_dic['denmark'])
    countries_dic['denmark'].side_countries.add(countries_dic['russia_east'])
    countries_dic['russia_east'].side_countries.add(countries_dic['denmark'])
    countries_dic['denmark'].side_countries.add(countries_dic['russia_east'])
    countries_dic['russia_east'].side_countries.add(countries_dic['europe_east'])
    countries_dic['europe_east'].side_countries.add(countries_dic['russia_east'])
    countries_dic['denmark'].side_countries.add(countries_dic['europe_east'])
    countries_dic['europe_east'].side_countries.add(countries_dic['denmark'])
    countries_dic['russia_east'].side_countries.add(countries_dic['russia_west'])
    countries_dic['russia_west'].side_countries.add(countries_dic['russia_east'])
    countries_dic['algeria'].side_countries.add(countries_dic['egypt'])
    countries_dic['egypt'].side_countries.add(countries_dic['algeria'])
    countries_dic['chad'].side_countries.add(countries_dic['egypt'])
    countries_dic['egypt'].side_countries.add(countries_dic['chad'])
    countries_dic['algeria'].side_countries.add(countries_dic['chad'])
    countries_dic['chad'].side_countries.add(countries_dic['algeria'])
    countries_dic['congo'].side_countries.add(countries_dic['chad'])
    countries_dic['chad'].side_countries.add(countries_dic['congo'])
    countries_dic['madagascar'].side_countries.add(countries_dic['congo'])
    countries_dic['congo'].side_countries.add(countries_dic['madagascar'])
    countries_dic['south_africa'].side_countries.add(countries_dic['congo'])
    countries_dic['congo'].side_countries.add(countries_dic['south_africa'])
    countries_dic['madagascar'].side_countries.add(countries_dic['south_africa'])
    countries_dic['south_africa'].side_countries.add(countries_dic['madagascar'])
    countries_dic['madagascar'].side_countries.add(countries_dic['australia'])
    countries_dic['australia'].side_countries.add(countries_dic['madagascar'])
    countries_dic['indonesia'].side_countries.add(countries_dic['australia'])
    countries_dic['australia'].side_countries.add(countries_dic['indonesia'])
    countries_dic['indonesia'].side_countries.add(countries_dic['india'])
    countries_dic['india'].side_countries.add(countries_dic['indonesia'])
    countries_dic['middle_east_israel'].side_countries.add(countries_dic['kazakhstan'])
    countries_dic['kazakhstan'].side_countries.add(countries_dic['middle_east_israel'])
    countries_dic['mongolia'].side_countries.add(countries_dic['russia_west'])
    countries_dic['russia_west'].side_countries.add(countries_dic['mongolia'])
    countries_dic['mongolia'].side_countries.add(countries_dic['china'])
    countries_dic['china'].side_countries.add(countries_dic['mongolia'])
    countries_dic['kazakhstan'].side_countries.add(countries_dic['russia_east'])
    countries_dic['russia_east'].side_countries.add(countries_dic['kazakhstan'])
    countries_dic['mongolia'].side_countries.add(countries_dic['kazakhstan'])
    countries_dic['kazakhstan'].side_countries.add(countries_dic['mongolia'])
    countries_dic['russia_west'].side_countries.add(countries_dic['kazakhstan'])
    countries_dic['kazakhstan'].side_countries.add(countries_dic['russia_west'])
    countries_dic['china'].side_countries.add(countries_dic['kazakhstan'])
    countries_dic['kazakhstan'].side_countries.add(countries_dic['china'])
    countries_dic['iran'].side_countries.add(countries_dic['middle_east_israel'])
    countries_dic['middle_east_israel'].side_countries.add(countries_dic['iran'])
    countries_dic['china'].side_countries.add(countries_dic['iran'])
    countries_dic['iran'].side_countries.add(countries_dic['china'])
    countries_dic['india'].side_countries.add(countries_dic['iran'])
    countries_dic['iran'].side_countries.add(countries_dic['india'])
    countries_dic['kazakhstan'].side_countries.add(countries_dic['iran'])
    countries_dic['iran'].side_countries.add(countries_dic['kazakhstan'])
    countries_dic['france'].side_countries.add(countries_dic['europe_east'])
    countries_dic['europe_east'].side_countries.add(countries_dic['france'])
    countries_dic['france'].side_countries.add(countries_dic['spain'])
    countries_dic['spain'].side_countries.add(countries_dic['france'])
    countries_dic['algeria'].side_countries.add(countries_dic['spain'])
    countries_dic['spain'].side_countries.add(countries_dic['algeria'])
    countries_dic['mexico'].side_countries.add(countries_dic['south_america_n'])
    countries_dic['south_america_n'].side_countries.add(countries_dic['mexico'])
    countries_dic['brazil'].side_countries.add(countries_dic['south_america_n'])
    countries_dic['south_america_n'].side_countries.add(countries_dic['brazil'])
    countries_dic['brazil'].side_countries.add(countries_dic['south_america_s'])
    countries_dic['south_america_s'].side_countries.add(countries_dic['brazil'])
    countries_dic['south_africa'].side_countries.add(countries_dic['south_america_s'])
    countries_dic['south_america_s'].side_countries.add(countries_dic['south_africa'])
    countries_dic['brazil'].side_countries.add(countries_dic['congo'])
    countries_dic['congo'].side_countries.add(countries_dic['brazil'])

    return countries_dic


def find_min_value_s_key(dic):
    """

    :param dic: dictionary which its values are numbers.
    :return: The key (the first one) of the minimum value.
    """
    min_value = dic[dic.keys()[0]]
    min_key = dic.keys()[0]
    for k, v, in dic.items():
        if v < min_value:
            min_value = v
            min_key = k
    return min_key


def change_mode(mode):
    """
    Changes the mode of the game and the instructions text.

    :param mode: *MODE
    :return: None
    """
    Game.MODE = mode
    Game.INSTRUCTIONS_LABEL.text = add_enter_in_instruction(Game.RES_DICT['inst_' + mode])
    print 'Mode changed to {}'.format(mode)


def add_enter_in_instruction(instruction, enter=25):
    """

    :param instruction: long string
    :param enter: Maximum chars in a line.
    :return: New string withe the \n in the correct places.
    """
    new_instruction = ''

    splt = instruction.split()

    temp = 0
    for word in splt:
        if len(word) + temp > enter:
            new_instruction += "\n"
            temp = 0
        new_instruction += word
        temp += len(word)
        new_instruction += " "

    return new_instruction


def are_side_blocs(bloc1, bloc2):
    """

    :param bloc1: *Bloc
    :param bloc2: *Bloc
    :return: True if bloc1 and bloc2 are adjacent to one another, else False
    """
    for country in bloc1:
        for side_country in country.side_countries:
            if side_country in bloc2:
                return True
    return False


def create_res_dict():
    """

    :return: Dictionary contains the sentences the program need to use from the resources file.
    """
    d = dict()
    with open("src.txt") as f:
        for line in f:
            if len(line) >= 2:
                key = ''
                value = ''
                for c in line:
                    if c != ':':
                        key += c
                    else:
                        break
                for c in line[len(key) + 2:len(line) - 1]:
                    value += c

                (k, v) = (key, value)
                d[k] = v
    return d


class Game(Layout, Image):
    RES_DICT = create_res_dict()

    # INSTRUCTIONS_MODE = dict()
    # INSTRUCTIONS_MODE['cc'] = 'Instructions:\n' + add_enter_in_instruction("Choose a country belongs to you")
    # INSTRUCTIONS_MODE['csc'] = 'Instructions:\n' + add_enter_in_instruction("Choose a country near the country you've just chose")
    # INSTRUCTIONS_MODE['aa'] = 'Instructions:\n' + add_enter_in_instruction("Choose how to divide your new armies (see above) between your countries")
    # INSTRUCTIONS_MODE['ct'] = 'Instructions:\n' + add_enter_in_instruction("Computer's turn")
    # INSTRUCTIONS_MODE['pa'] = 'Instructions:\n' + add_enter_in_instruction("Choose how many armies you want to pass to this country from the previous country") # Pass Armies

    INSTRUCTIONS_LABEL = Label(text='Instructions:\nChoose a country belongs to you',
                               bold=True,
                               font_size=20,
                               pos=(1060, 500),
                               halign="center",
                               valign="middle",
                               color=(0, 0, 0, 1))
    NO_ARMIES_IN_CHOSE_COUNTRY_TEXT = add_enter_in_instruction(
        "You don't have armies to pass from the country you chose before. close it to continue.")
    NO_ARMIES_IN_CHOSE_COUNTRY_LABEL = Label(text="",
                                             text_size=(None, None),
                                             font_size=20,
                                             pos=(1060, 550),
                                             size_hint_y=None,
                                             halign="center",
                                             valign="middle",
                                             color=(214.0/256, 111.0/256, 111.0/256, 1))
    NOT_USER_COUNTRY_TEXT = add_enter_in_instruction("This country doesn't belongs to you.")
    NOT_USER_COUNTRY_LABEL = Label(text="",
                                   text_size=(None, None),
                                   font_size=20,
                                   pos=(1080, 600),
                                   size_hint_y=None,
                                   halign="center",
                                   valign="middle",
                                   color=(0, 0, 0, 1))
    ARMIES_LABEL = Label(text='5',
                         size=(100, 100),
                         pos=(1100, 770),
                         markup=True,
                         font_size=40,
                         color=(0, 10, 1, 1))
    ARMIES_LABEL_TRY = Label(text='5',
                             size=(100, 100),
                             pos=(950, 770),
                             markup=True,
                             font_size=40,
                             color=(0, 10, 1, 1))
    YELLOW_SQUARE = None

    MODE = 'aa'  # Look at the file's documentation *Mode

    ADDITION_ARMIES = 5
    USER_NAME = ''

    def __init__(self, countries_dic, **kwargs):
        """
        Creats a Game object.

        :param countries_dic: Dictionary contains all the Game's countries:
            keys -> Countries's name.
            values -> Country objects.
        """
        Image.__init__(self)
        Layout.__init__(self)

        self.source = 'world_map_draw_the_limit.png'

        self.finish_turn_btn = Button(text='Start Tutorial',
                                      size=(180, 30),
                                      pos=(100, 10),
                                      halign="center",
                                      markup=True,
                                      font_size=25)
        self.play_btn = Button(text='PLAY !',
                               size=(150, 30),
                               pos=(500, 500),
                               halign="center",
                               markup=True,
                               font_size=25)
        self.hide_instructions = Button(text='Hide Instructions',
                                        bold=True,
                                        radius=[50, ],
                                        size=(170, 30),
                                        pos=(1050, 460),
                                        halign="center",
                                        border=(30, 30, 30, 30),
                                        background_normal='blue.png',
                                        markup=True,
                                        font_size=20)
        self.hide_instructions.bind(on_press=self.hide_instructions_click)
        self.info_btn = ImageButton('help_icon.png', self.info_click, size=(50, 50), pos=(30, 820))
        self.finish_turn_btn.bind(on_press=self.click_finish_turn)
        self.add_widget(self.finish_turn_btn)
        self.play_btn.bind(on_press=self.play_btn_click)
        self.add_widget(self.play_btn)
        self.add_widget(Game.NO_ARMIES_IN_CHOSE_COUNTRY_LABEL)
        self.add_widget(Game.NOT_USER_COUNTRY_LABEL)

        self.countries_dic = countries_dic

        self.popup = Popup(title='Test popup',
                           size_hint=(None, None), size=(1024, 512), auto_dismiss=False)
        self.popup.title_color = self.popup.separator_color
        self.popup.background = 'wall.jpg'
        self.popup.bind(on_dismiss=self.dismiss_popup)

        # Countries and their poses
        """
        '''
        self.add_widget(Country(2, [], 1, (620, 495)))  # Egypt
        self.add_widget(Country(1, [], 5, (245, 610)))  # Usa East
        self.add_widget(Country(2, [], 5, (124, 623)))  # USA West
        self.add_widget(Country(0, [], 5, (228, 770)))  # Canada
        self.add_widget(Country(1, [], 1, (993, 168)))  # Australia
        self.add_widget(Country(1, [], 2, (689, 708)))  # Russia East
        self.add_widget(Country(2, [], 2, (916, 777)))  # Russia West
        self.add_widget(Country(0, [], 3, (540, 640)))  # France
        self.add_widget(Country(2, [], 3, (514, 596)))  # Spain
        self.add_widget(Country(0, [], 2, (799, 481)))  # India
        self.add_widget(Country(1, [], 2, (655, 543)))  # Middle East (Israel Area)
        self.add_widget(Country(2, [], 1, (600, 670)))  # Europe East
        self.add_widget(Country(0, [], 2, (868, 583)))  # China
        self.add_widget(Country(0, [], 5, (151, 520)))  # Mexico
        self.add_widget(Country(1, [], 5, (242, 384)))  # South America (N)
        self.add_widget(Country(1, [], 5, (304, 103)))  # South America (S)
        self.add_widget(Country(2, [], 5, (321, 281)))  # Brazil
        self.add_widget(Country(2, [], 3, (613, 779)))  # Denmark
        self.add_widget(Country(1, [], 1, (536, 509)))  # Algeria
        self.add_widget(Country(0, [], 1, (602, 330)))  # Congo
        self.add_widget(Country(0, [], 1, (690, 228)))  # Madagascar
        self.add_widget(Country(0, [], 1, (605, 213)))  # South Africa
        self.add_widget(Country(2, [], 5, (487, 846)))  # Greenland
        self.add_widget(Country(1, [], 1, (585, 436)))  # Chad
        self.add_widget(Country(2, [], 0, (937, 342)))  # Indonesia
        '''

        # 620, 495 - Egypt              V
        # 245, 610 - USA East           V
        # 124, 623 - USA West           V
        # 228, 770 - Canada             V
        # 993, 168 - Australia          V
        # 689, 708 - Russia East        V
        # 916, 777 - Russia West        V
        # 540, 640 - France             V
        # 514, 596 - Spain              V
        # 799, 481 - India              V
        # 655, 543 - Israel area (- Middle East)    V
        # 614, 679 - Europe East        V
        # 868, 583 - China              V
        # 151, 520 - Mexico             V
        # 242, 384 - South America (N)  V
        # 304, 103 - South America (S)  V
        # 321, 281 - Brazil             V
        # 613, 779 - Denmark            V
        # 536, 509 - Algeria            V
        # 602, 330 - Congo              V
        # 690, 228 - Madagascar         V
        # 605, 213 - South Africa       V
        # 487, 846 - Greenland          V
        # 585, 436 - Chad               V
        # 937, 342 - Indonesia          V
        """

    def start_game(self):
        # Add all countries to the map
        for country in self.countries_dic.values():
            self.add_widget(country)
        self.finish_turn_btn.text = 'Finish My Turn'

    def dismiss_popup(self, instance):
        """
        Calls when the popup is dismissed.
        Clear all the Instructions things.
        """
        return False

    def play_btn_click(self, t):
        """
        Handle a click on Play button
        """
        self.popup.dismiss()
        if Game.ARMIES_LABEL_TRY.parent:
            self.remove_widget(Game.ARMIES_LABEL_TRY)
        self.start_game()
        self.remove_widget(self.play_btn)
        if not Game.ARMIES_LABEL.parent:
            self.add_widget(Game.ARMIES_LABEL)
        self.add_widget(self.info_btn)
        self.add_widget(Game.INSTRUCTIONS_LABEL)
        self.add_widget(self.hide_instructions)
        if self.info_btn.parent:
            self.remove_widget(self.info_btn)

    def info_click(self, t):
        """
        Handle click on info button.
        Closes the small Info button and shows the instructions.
        """
        self.add_widget(Game.INSTRUCTIONS_LABEL)
        self.add_widget(self.hide_instructions)
        self.remove_widget(self.info_btn)

    def hide_instructions_click(self, t):
        """
        Handle click on Hide Info button.
        Closes the instructions and shows the small info button
        """
        self.remove_widget(Game.INSTRUCTIONS_LABEL)
        self.remove_widget(self.hide_instructions)
        self.add_widget(self.info_btn)

    @staticmethod
    def refresh_addition_armies_label(number):
        """
        This function refreshes the label which shows the number of armies that the user can share in every turn.
        :param number: number od armies to share between all user's countries
        :return: None
        """
        if number == 0:
            Game.ADDITION_ARMIES = 5
            change_mode('cc')
            Game.ARMIES_LABEL.text = '0'
            return
        Game.ADDITION_ARMIES = number
        Game.ARMIES_LABEL.text = str(number)

    def pass_armies(self, source_country, armies_number, des_country):
        """
        This function passes [armies_number] armies from source_country to des_country

        :param source_country: Country object - from this country the armies is coming
        :param armies_number: int - number of the armies to pass
        :param des_country: Country object - to this country the armies is coming
        :return:
        """

        # Input Checking
        if source_country.control != 1:
            print 'Error! in pass_armies, the source country must to belong to the computer'
            return
        if armies_number < 0:
            armies_number = abs(armies_number)
        if armies_number > abs(source_country.armies_counter):
            print 'Input warn ! pass_armies'
            armies_number = abs(source_country.armies_counter)

        if des_country.control == 0:  # neutral country
            if abs(des_country.armies_counter) >= armies_number:  # Can't conquer, only passing
                des_country.refresh_armies_counter(des_country.armies_counter + armies_number)
            else:  # Conquer !
                des_country.refresh_armies_counter(-(armies_number - abs(des_country.armies_counter)))
                des_country.change_control(1)

        else:  # User / Computer
            des_country.refresh_armies_counter(des_country.armies_counter - armies_number)
            if des_country.control == 2 and des_country.armies_counter < 0:  # Change to computer's control
                des_country.change_control(1)

        source_country.refresh_armies_counter(source_country.armies_counter + armies_number)
        if armies_number != 0:
            print "Country {} passed {} armies to country {}".format(self.country_name(source_country).upper(),
                                                                     armies_number,
                                                                     self.country_name(des_country).upper())

    def country_name(self, country):
        """

        :param country: Country object in the game.
        :return: Name of the country in the countries_dic. --> string.
                or None if not found.
        """
        for name, c in self.countries_dic.items():
            if country == c:
                return name

    def country_bloc(self, root_country, past_countries=None):
        """

        :param past_countries: The countries which is already in the bloc.
        :param root_country: Country object, begins the bloc.
        :return: List, contains all countries in the *Bloc, Included the root country.
        """

        if past_countries is None:
            past_countries = []
        if root_country.control == 0:
            return [root_country]
        if root_country not in past_countries:
            past_countries.append(root_country)
        the_bloc = past_countries
        for side_country in root_country.side_countries:
            if (side_country not in past_countries) and (side_country.control == root_country.control):
                the_bloc += self.country_bloc(root_country=side_country, past_countries=past_countries)

        return list(set(the_bloc))

    def all_blocs_in_game(self):
        """
        :return: List contains all the *Blocs in the game right now.
        """

        all_blocs = list()
        past_countries = list()
        for country in self.countries_dic.values():  # All countries
            if country not in past_countries:
                all_blocs.append(self.country_bloc(root_country=country))  #
                past_countries += self.country_bloc(root_country=country)
        return all_blocs

    def list_of_likelihood_countries(self, bloc1, bloc2):
        """

        :param bloc1: *Bloc
        :param bloc2: *Bloc
        :return: List of the countries which are side for bloc1 and part of bloc2.
        """
        the_list = list()
        for country1 in bloc1:
            for side_country in self.countries_dic[self.country_name(country=country1)].side_countries:
                if side_country in bloc2:
                    the_list.append(side_country)
        return the_list

    def bloc_side_blocs(self, bloc):
        """

        :param bloc: *Bloc
        :return: All the blocs near the giving bloc.
        """
        the_side_blocs = list()
        for ex_country in ext_countries_in_bloc(bloc=bloc):  # All the ext-countries in the bloc.
            for side_country in ex_country.side_countries:  # All the side countries to the country.
                if side_country.control != ex_country.control:  # The side country not in the bloc.
                    if list(set(self.country_bloc(root_country=side_country))) \
                            not in the_side_blocs:  # if the bloc not exist yet.
                        the_side_blocs.append(list(set(self.country_bloc(root_country=side_country))))
        return the_side_blocs

    def user_blocs(self):
        # Returns all the user's *blocs in the game.
        return list(filter(lambda x: x[0].control == 2, self.all_blocs_in_game()))

    def computer_blocs(self):
        # Returns all the computer's *blocs in the game.
        return list(filter(lambda x: x[0].control == 1, self.all_blocs_in_game()))

    def new_game(self):
        """
        Initialize the board to game start position.
        """
        for c in self.countries_dic.values():
            self.remove_widget(c)
        self.countries_dic = create_start_countries_dict()
        for c in self.countries_dic.values():
            self.add_widget(c)

        change_mode('cc')

    def yes_click(self, t):
        # Handle the click on the 'Yes' button in the popup when the game ends.
        print "New Game !"
        self.new_game()
        self.popup.dismiss()
        self.finish_turn_btn.text = 'Finish my turn'
        Game.ARMIES_LABEL.text = '0'

    def no_click(self, t):
        # Handle the click on the 'No' button in the popup when the game ends.
        self.popup.dismiss()

    def win_popup(self, winner):
        """
        Shows popup with the correct title, question (Do you want to play again?) and two optional answers: Yes\No.
        Note: The user can click out of the popup window and it will be closed.

        :param winner: The player who won the game --> 1=Computer; 2=User
        """
        # Winner can be 1 OR 2 ONLY

        if winner == 1:
            tit = 'Game Over'
            mes = 'I am the winner !! HAHA'
            winner_color = (1, 0, 0, 1)
        else:
            tit = 'You are the WINNER !'
            mes = 'My congratulations! You won !'
            winner_color = (0, 0, 1, 1)

        self.popup.title = tit

        main_grid = GridLayout(rows=3, cols=1)

        main_grid.add_widget(Label(text=mes, font_size=30, halign="center", valign="middle", color=(0, 0, 0, 1)))
        question_content = Label(text='Do you want to play again?', font_size=25, halign="center", color=(0, 0, 0, 1))
        main_grid.add_widget(question_content)

        grid_content = GridLayout(rows=1, cols=2)
        content_yes = Button(text='Yes', size_hint_y=None, height=40, font_size=20)
        content_no = Button(text='No', size_hint_y=None, height=40, font_size=20)
        content_no.bind(on_press=self.no_click)
        content_yes.bind(on_press=self.yes_click)
        grid_content.add_widget(content_yes)
        grid_content.add_widget(content_no)

        main_grid.add_widget(grid_content)
        self.popup.content = main_grid
        self.popup.background = 'winner.jpg'
        self.popup.background_color = winner_color
        self.popup.separator_color = winner_color
        self.popup.title_color = (1, 0, 0, 1)
        self.popup.open()

    def is_win(self):
        """
        Checks if there is a win.
        That's mean - The user does'nt have any country OR the computer dose'nt have any country.

        :return: Tuple(boolean, int):   If the boolean is True --> There is a winner.
                                        the int shows WHO is the winner (0-No winner; 1-Computer, 2-User).

        """
        if not self.user_blocs():
            return True, 1
        elif not self.computer_blocs():
            return True, 2
        else:
            return False, 0

    def click_finish_turn(self, touch):
        """
        Handle the 'finish turn' button click.
        The user clicks the FINISH button when he finish his turn.
        So, in this function, all the user-turn parameters are initialized.

        *Note: At the beginning of the game this function hands the 'start tutorial' button's click.
        """

        if self.finish_turn_btn.text == 'Start Tutorial':
            self.refresh_popup('MAIN')
            return
        # Win check
        if self.is_win()[0]:
            self.win_popup(self.is_win()[1])
            self.finish_turn_btn.text = 'Start Over'
            return

        # Finish User turn:
        if Country.CHOSE_COUNTRY:
            Country.CHOSE_COUNTRY.country_click(0)
        Country.CHOSE_COUNTRY = None
        Country.TARGET_COUNTRY = None
        Game.NOT_USER_COUNTRY_LABEL.text = ''

        print "user finishes his turn,\nnow computer turn"

        # Start Computer turn:
        change_mode('ct')
        self.computer_turn()

        # Win check
        if self.is_win()[0]:
            self.win_popup(self.is_win()[1])
            self.finish_turn_btn.text = 'Start Over'
            return

    def computer_turn(self):
        """
        Finish the user's turn.
        Handle the computer turn (The AI functions).
        Finish the computer's turn.
        """

        # Computer's turn
        Game.ARMIES_LABEL.text = "Computer Turn"
        self.ai_divide_armies_between_blocs()
        self.ai_attack()

        # Computer finished his turn.
        print "Computer finished his turn,\nnow user turn"
        Country.OCCUPIED_COUNTRIES = []
        change_mode('aa')
        Game.ARMIES_LABEL.text = '5'
        Game.ADDITION_ARMIES = 5

    # UNUSED METHODS
    '''
    def all_options_to_divide_armies_between_blocs(self, armies_to_divide=5):
        """
        The function returns all the options to divide armies_to_divide between computer's blocs.
        :param armies_to_
        divide:
        :return: All the options to divide the armies between computer's blocs.
                    In the structer below:
                        [(0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0)]
                        [Option(0), Option(1),...]
                        Option(N) = Tuple --> (Bloc(0), Bloc(1)...)
        """

        if len(self.computer_blocs()) == 1:
            return [(armies_to_divide)]

        # ELSE
        temp = list()
        for x in range(armies_to_divide + 1):
            temp.append(x)
        # temp = [0,1,2,3,4,5]

        all_options = permutations(temp, len(self.computer_blocs()))
        all_options = filter(lambda option: sum(option) == 5, all_options)
        return all_options
    '''
    '''
    def find_bloc_by_name(self, name):
        """

        :param name: A string represents the name of the first country in the bloc.
        :return: The *bloc, or None, if wasn't found.
        """
        for bloc in self.all_blocs_in_game():
            if self.country_name(bloc[0]) == name:
                return bloc
        return None
    '''
    # Before Game:
    # def before_game(self):
    #     content1 = Label(text="Hello", font_size=30)
    #     content2 = Label(text="What is your name?", font_size=25)
    #     content3 = TextInput(multiline=False, font_size=25)
    #     content4 = Button(text='SUBMIT', font_size=20)
    #
    #     content4.bind(on_press=self.submit_click)
    #
    #     main_content = GridLayout(rows=4, cols=1)
    #     main_content.add_widget(content1)
    #     main_content.add_widget(content2)
    #     main_content.add_widget(content3)
    #     main_content.add_widget(content4)
    #
    #     self.popup.title = 'INSTRUCTIONS'
    #     self.popup.content = main_content
    #     self.popup.open()
    """
        def before_next_moves_list(self):
            after_divide_and_attack_list = list()
            final_list = list()
            divide_options = self.all_options_to_divide_armies_between_blocs()


            # [[NameRepresents1: (SumArmies1, Control1, countries_number1), NameRepresents2: (SumArmies2, Control2, countries_number2)], [NameRepresents1'; (SumArmies1', Control1', countries_number1')]]

            # Divide !
            for option in divide_options:  # All divide options
                index = 0  # The side bloc index
                after_divide_op_dict = dict()  # All the blocs in the game showed in tuples.
                after_attack_dict = dict()

                bloc_index = 0
                for bloc in self.all_blocs_in_game():  # All blocs in the game
                    bloc_name = self.country_name(bloc[0])
                    control = bloc[0].control

                    bloc_sum_armies = sum_armies_in_bloc(bloc=bloc)
                    bloc_countries_number = len(bloc)

                    all_blocs_copy = copy_all_blocs(self.all_blocs_in_game())

                    if control != 1:  # Not computer's bloc
                        after_divide_op_dict[bloc_name] = (bloc_sum_armies, control, bloc_countries_number)

                    else:  # Only computer's blocs
                        saver_bloc_countries_number = len(bloc)

                        # Initiate the added_armies_to_comp_bloc --> How many armies this computer's bloc need to get.
                        try:
                            added_armies_to_comp_bloc = option[index]
                        except TypeError:
                            added_armies_to_comp_bloc = option

                        # Add the armies... NEGATIVE
                        bloc_sum_armies -= added_armies_to_comp_bloc
                        # TODO(3): Change the random here
                        rand_country = all_blocs_copy[bloc_index][randrange(len(all_blocs_copy[bloc_index]))]
                        rand_country.armies_counter -= added_armies_to_comp_bloc

                        after_divide_op_dict[bloc_name] = (bloc_sum_armies, control, bloc_countries_number)

                        # All the Options to Attack --> Tuples... every tuple's length is the length of the bloc's side_blocs.
                        attack_options = filter(lambda x: sum(x) <= abs(bloc_sum_armies),
                                                list(itertools.product(range(abs(bloc_sum_armies) + 1),
                                                                       repeat=len(self.bloc_side_blocs(bloc=bloc)))))

                        for attack_option in attack_options:  # Tuples...
                            attack_index = 0  # The index in the attack_option (tuple)

                            # Back to the beginning, after the adding.
                            bloc_sum_armies = sum_armies_in_bloc(bloc=bloc) - added_armies_to_comp_bloc


                            bloc_countries_number = saver_bloc_countries_number

                            for side_bloc in self.bloc_side_blocs(bloc=bloc):  # all the side_blocs
                                if attack_option[attack_index] == 0:  # We don't have to attack this bloc
                                    continue

                                # We have to attack this bloc
                                side_bloc_sum_armies = sum_armies_in_bloc(bloc=side_bloc)
                                armies_to_pass_to_this_bloc = attack_option[attack_index]

                                print 'BEFORE', side_bloc_sum_armies, bloc_sum_armies, armies_to_pass_to_this_bloc

                                # Side bloc details:
                                side_bloc_control = side_bloc[0].control
                                side_bloc_countries_number = len(side_bloc)

                                if abs(side_bloc_sum_armies)+1 <= armies_to_pass_to_this_bloc:  # Must attack this bloc !

                                    if side_bloc_control == 2:  # User's bloc
                                        likely_countries_list = list()

                                        for likely_country in self.list_of_likelihood_countries(bloc1=bloc,
                                                                                                bloc2=side_bloc):
                                            likely_countries_list.append(likely_country)
                                            if likely_country.armies_counter+1 <= armies_to_pass_to_this_bloc:

                                                # Refresh computer_bloc
                                                bloc_sum_armies += (likely_country.armies_counter + 1)
                                                bloc_countries_number += 1

                                                # Refresh side_bloc:
                                                side_bloc_sum_armies -= likely_country.armies_counter
                                                side_bloc_countries_number -= 1

                                                # Refresh 'armies to pass to this bloc'
                                                armies_to_pass_to_this_bloc -= (likely_country.armies_counter + 1)

                                    elif side_bloc_control == 0:  # neutral bloc

                                        if abs(side_bloc_sum_armies) + 1 <= armies_to_pass_to_this_bloc:  # Can attack!

                                            # Refresh computer_bloc
                                            bloc_sum_armies += (abs(side_bloc_sum_armies) + 1)
                                            bloc_countries_number += 1

                                            # Refresh side_bloc:
                                            side_bloc_sum_armies -= side_bloc_sum_armies
                                            side_bloc_countries_number -= 1

                                            # Refresh 'armies to pass to this bloc'
                                            armies_to_pass_to_this_bloc -= (abs(side_bloc_sum_armies) + 1)

                                attack_index += 1

                                # HERE  - Add the side_bloc.
                                print 'AFTER', side_bloc_sum_armies, bloc_sum_armies, self.country_name(side_bloc[0]), bloc_name

                                the_side_bloc = (side_bloc_sum_armies, side_bloc_control, side_bloc_countries_number)
                                if side_bloc_countries_number or True:  # Not an empty bloc
                                    after_attack_dict[self.country_name(side_bloc[0])] = the_side_bloc

                            # Here - Add the bloc.

                            after_attack_dict[bloc_name] = (bloc_sum_armies, control, bloc_countries_number)

                            after_divide_and_attack_list.append(copy.deepcopy(after_attack_dict))

                        index += 1
                    bloc_index += 1

            print 'aaaaaaaaaaaaaaa', len(after_divide_and_attack_list)
            after_divide_and_attack_list = reduce_list_of_dicts(list_of_dicts=after_divide_and_attack_list)
            print 'bbbbbbbbbbbbbbb', len(after_divide_and_attack_list)

            return after_divide_and_attack_list
        def list_next_moves(self):

            # TODO(History): Match to the blocs names and countries.. -> Show all boards !

            the_list = self.before_next_moves_list()
        """

    def how_many_armies_to_add(self, bloc):
        """
        Returns the number of armies that the (computer's) bloc need to **win the side user's blocs.
            ** Win a side bloc means - have at least one more army than the side bloc.
        :param bloc: computer's *Bloc
        :return: List of positive numbers.
            Note: Every number represents a number of armies the computer need to conquer a side bloc.
        """
        # Input Check
        if bloc[0].control != 1:
            return None
        side_countries_hefreshim = list()
        bloc_sum_armies = abs(sum_armies_in_bloc(bloc=bloc))

        for side_bloc in self.bloc_side_blocs(bloc=bloc):
            if side_bloc[0].control == 2:  # User's bloc
                side_bloc_sum_armies = abs(sum_armies_in_bloc(bloc=side_bloc))
                if side_bloc_sum_armies >= bloc_sum_armies:
                    side_countries_hefreshim.append(side_bloc_sum_armies - bloc_sum_armies + 1)
        return side_countries_hefreshim

    def try_it_click(self, t):
        # Try btn callback. In thetutorial.
        self.refresh_popup('TRY ADD ARMIES')
        return

    def refresh_popup(self, title):
        """
        Refreshes the popup according its title.

        :param title: The title of the popup
        :return: None
        """

        if title == 'MAIN':
            content1 = Label(text="Hello", font_size=40, color=(0, 0, 0, 1))
            content2 = Label(text="What is your name?", font_size=25, halign="center", color=(0, 0, 0, 1))

            content3 = TextInput(multiline=False, font_size=25)
            content3.text = Game.USER_NAME
            print "Size = ", content3.size
            content3.padding_x = content3.size[0] / 2
            content3.padding_y = 10

            content4 = Button(text='SUBMIT', font_size=20)
            content4.bind(on_press=self.next_popup)

            main_content = GridLayout(rows=4, cols=1)
            main_content.add_widget(content1)
            main_content.add_widget(content2)
            main_content.add_widget(content3)
            main_content.add_widget(content4)

            self.popup.title = 'INSTRUCTION'
            self.popup.content = main_content
            self.popup.open()

        elif title == 'PAGE 1':
            self.popup.title = title
            print 'USER NAME = ', Game.USER_NAME
            content1 = Label(
                text="Hi {},\nWelcome to Raz's War Game.\nIn this game your goal is to conquer the world.\n"
                     "We are going to play 1X1 on the whole world !".
                    format(Game.USER_NAME),
                font_size=20, halign="center", color=(0, 0, 0, 1), size_hint_y=10)
            content2 = Label(text='Your countries are BLUE', font_size=18,
                             color=(75.0 / 256, 166.0 / 256, 256.0 / 256, 1), size_hint_y=5)
            content3 = Label(text='My countries are RED', font_size=18,
                             color=(1, 0, 0, 1), size_hint_y=5)
            content4 = Label(text='And the neutral countries are GREEN', font_size=18,
                             color=(62.0 / 256, 134.0 / 256, 69.0 / 256, 1), size_hint_y=5)
            content5 = Label(text='*Note:'
                                  ' Above any country there is a number'
                                  ' symbolizes the number of armies in the country.',
                             font_size=22, color=(1, 1, 0, 1), halign="left", size_hint_y=5)
            content6 = GridLayout(row=1, cols=2, size_hint_y=4)
            content61 = Button(text='BACK', font_size=22, color=(0, 0, 0, 1))
            content61.bind(on_press=self.previous_popup)
            content62 = Button(text='OK, Next', font_size=22, color=(1, 1, 1, 1))
            content62.bind(on_press=self.next_popup)
            content6.add_widget(content61)
            content6.add_widget(content62)
            main_content = GridLayout(rows=6, cols=1)
            main_content.add_widget(content1)
            main_content.add_widget(content2)
            main_content.add_widget(content3)
            main_content.add_widget(content4)
            main_content.add_widget(content5)
            main_content.add_widget(content6)

            self.popup.content = main_content

        elif title == 'PAGE 2':
            self.popup.title = title

            who_win_content = Label(text='[b]' + add_enter_in_instruction(Game.RES_DICT['who_win'], 60) + '[/b]',
                                    font_size=32, size_hint_y=10, color=(.2, .21, .8, 1), markup=True)

            content1 = GridLayout(rows=1, cols=2)
            content11 = Button(text='BACK', size_hint_y=1, font_size=18, color=(0, 0, 0, 1))
            content11.bind(on_press=self.previous_popup)
            content12 = Button(text='OK, NEXT', size_hint_y=1,
                               font_size=18, color=(1, 1, 1, 1))
            content12.bind(on_press=self.next_popup)
            content1.add_widget(content11)
            content1.add_widget(content12)

            main_content = GridLayout(rows=2, cols=1)
            main_content.add_widget(who_win_content)
            main_content.add_widget(content1)
            self.popup.content = main_content

        elif title == 'PAGE 3':
            self.popup.title = 'PAGE 3'

            if not Game.ARMIES_LABEL_TRY.parent:
                Game.YELLOW_SQUARE = ImageButton(source='yellow.png', click_fun=None, pos=(950, 770),
                                                 size=Game.ARMIES_LABEL.size)
                self.add_widget(Game.YELLOW_SQUARE)
                self.add_widget(Game.ARMIES_LABEL_TRY)

            content1 = GridLayout(rows=1, cols=2, size_hint_x=50)
            content1.add_widget(Label(size_hint_x=1))  # Margin...
            content12 = Label(
                text=add_enter_in_instruction(Game.RES_DICT['at_beginning_add'], 50) + '\n' +
                     add_enter_in_instruction(Game.RES_DICT['where_armies_label'], enter=50),
                halign="left", font_size=22, color=(0, 0, 0, 1), size_hint_x=4)
            content1.add_widget(content12)
            content2 = Image(source='arrow_yellow.png', size_hint_x=35, size_hint_y=30)

            content3 = GridLayout(rows=1, cols=2, size_hint_y=3)
            content31 = Button(text='BACK', font_size=22, size_hint_x=2, color=(0, 0, 0, 1))
            content31.bind(on_press=self.previous_popup)
            content3.add_widget(content31)
            content3.add_widget(Label(size_hint_x=5))

            content4 = GridLayout(rows=2, cols=2, size_hint_y=3)
            content42 = Button(text='Next', font_size=22)
            content42.bind(on_press=self.next_popup)
            content41 = Button(text='Try It', font_size=22, color=(1, 1, 0, 1))
            content41.bind(on_press=self.try_it_click)
            content4.add_widget(content41)
            content4.add_widget(content42)

            main_content = GridLayout(rows=2, cols=2)
            main_content.add_widget(content1)
            main_content.add_widget(content2)
            main_content.add_widget(content3)
            main_content.add_widget(content4)
            self.popup.content = main_content

        elif title == 'TRY ADD ARMIES':
            self.popup.title = title
            main_content = FloatLayout(size=(1000, 500))

            content1 = Country(2, [], 2, (500, 500), 5, is_tot=True)
            change_mode('aa')

            # TODO(2): Change the button to imageButton.
            content2 = Button(text='Back', pos=(130, 225), font_size=25, size_hint=(.25, .08), color=(0, 0, 0, 1))
            content2.bind(on_press=self.previous_popup)

            content3 = Label(text='[b]You can add armies till the number at the right-top corner is 0.[/b]',
                             font_size=30, pos=(500, 350), color=(1, 1, 0, 1), markup=True)

            main_content.add_widget(content1)
            main_content.add_widget(content2)
            main_content.add_widget(content3)
            self.popup.content = main_content

        elif title == 'PAGE 4':  # Tutorial !

            if Game.ARMIES_LABEL_TRY.parent:
                self.remove_widget(Game.ARMIES_LABEL_TRY)
            if Game.YELLOW_SQUARE:
                self.remove_widget(Game.YELLOW_SQUARE)
                Game.YELLOW_SQUARE = None

            change_mode('cc')

            self.popup.title = 'PAGE 4'
            main_content = GridLayout(rows=7, cols=1)
            content1 = Label(
                text=add_enter_in_instruction(Game.RES_DICT['tot_p4_main'], 60) +
                '\n*Double click on the same country - will close it.',
                font_size=20, color=(0, 0, 0, 1), halign="left", size_hint_y=30)
            note_content1 = Label(
                text=Game.RES_DICT['short_cut_numbers'],
                color=(1, 1, 0, 1), font_size=18, halign="left", size_hint_y=10)
            note_content2 = Label(
                text=Game.RES_DICT['short_cut_space'],
                color=(1, 1, 0, 1), font_size=18, halign="left", size_hint_y=10)




            content2 = GridLayout(rows=5, cols=1, size_hint_y=15)
            content21 = Label(text='Pass to your other country which is near the first country: ',
                             color=(0, 0, 0, 1), font_size=18, halign='left')
            content2.add_widget(content21)
            country1 = Country(2, [], 2, (600, 490), is_tot=True, armies_counter=3)
            country2 = Country(2, [country1], 2, (500, 490), is_tot=True, armies_counter=2)
            country3 = Country(2, [country1], 2, (700, 490), is_tot=True, armies_counter=1)
            country1.side_countries = [country2, country3]
            content2.add_widget(country1)
            content2.add_widget(country2)
            content2.add_widget(country3)

            content3 = Label(text='Pass to other countries and decrease their armies counter or conquer them: ',
            #                   # TODO(1) Chage this text font_size "\n*In the game, country you've just conquered would be yours only in the next turn.",
                              color=(0, 0, 0, 1), font_size=18, halign='left', size_hint_y=15)

            content4 = GridLayout(rows=1, cols=3, size_hint_y=15)
            country4 = Country(2, [], 2, (600, 395), is_tot=True, armies_counter=7)
            country5 = Country(1, [country4], 2, (700, 395), is_tot=True, armies_counter=3)
            country6 = Country(0, [country4], 2, (500, 395), is_tot=True, armies_counter=1)
            country4.side_countries = [country5, country6]
            content4.add_widget(country4)
            content4.add_widget(country5)
            content4.add_widget(country6)

            content5 = GridLayout(rows=1, cols=2, size_hint_y=10)
            content51 = Button(text='BACK', font_size=22, color=(0, 0, 0, 1))
            content52 = Button(text='NEXT', font_size=22)
            content51.bind(on_press=self.previous_popup)
            content52.bind(on_press=self.next_popup)

            content5.add_widget(content51)
            content5.add_widget(content52)

            main_content.add_widget(content1)
            main_content.add_widget(content2)
            main_content.add_widget(content3)
            main_content.add_widget(content4)

            main_content.add_widget(note_content1)
            main_content.add_widget(note_content2)

            main_content.add_widget(content5)

            self.popup.content = main_content

        elif title == 'PAGE 5':
            self.popup.title = title
            main_content = GridLayout(rows=5, cols=1)
            content1 = Label(
                text=add_enter_in_instruction('[b]When you finish your turn, click on the button in the left-bottom corner- "Finish My Turn"[/b]', 30),
                font_size=35, halign='center', color=(.2, .21, .8, 1), markup=True, size_hint_y=100)

            content5 = GridLayout(rows=1, cols=2, size_hint_y=10)
            content51 = Button(text='BACK', font_size=22, color=(0, 0, 0, 1))
            content52 = Button(text='NEXT', font_size=22)
            content51.bind(on_press=self.previous_popup)
            content52.bind(on_press=self.next_popup)

            content5.add_widget(content51)
            content5.add_widget(content52)

            main_content.add_widget(content1)
            main_content.add_widget(content5)
            self.popup.content = main_content

        elif title == "LET'S PLAY":
            self.popup.title = title
            main_content = FloatLayout()
            lets_play_btn = ImageButton(source='crossed_swords.jpg', click_fun=self.play_btn_click, pos=(500, 500), size=(1000,1000))
            self.popup.content = lets_play_btn
            # TODO(!) Continue from here !

    def previous_popup(self, t):
        """
        Changes the popup to the previous look.
        """
        if self.popup.title == 'PAGE 1':
            self.refresh_popup('MAIN')
        elif self.popup.title == 'PAGE 2':
            self.refresh_popup('PAGE 1')
        elif self.popup.title == 'PAGE 3':
            self.refresh_popup('PAGE 2')
        elif self.popup.title == 'TRY ADD ARMIES':
            self.refresh_popup('PAGE 3')
        elif self.popup.title == 'PAGE 4':
            self.refresh_popup('PAGE 3')
        elif self.popup.title == 'PAGE 5':
            self.refresh_popup('PAGE 4')

    def next_popup(self, t):
        """
        Handle the popup's buttons_click...
              Sends the user to the next popup screen.
        """

        if self.popup.title == 'PAGE 1':
            # Open page 2.
            self.refresh_popup('PAGE 2')
            return

        elif self.popup.title == 'PAGE 2':
            # Open PAGE 3
            self.refresh_popup('PAGE 3')
            return

        elif self.popup.title == 'PAGE 3':
            # Move to PAGE 4 - The tutorial
            self.refresh_popup('PAGE 4')
            return

        elif self.popup.title == 'PAGE 4':
            # Open PAGE 5
            self.refresh_popup('PAGE 5')
            return

        elif self.popup.title == 'PAGE 5':
            # Go To Play
            self.refresh_popup("LET'S PLAY")
            return

        elif t.text == 'SUBMIT':
            # Save User name and continue to page 1.
            Game.USER_NAME = self.popup.content.children[1].text
            self.refresh_popup('PAGE 1')
            print 'USER NAME = ', Game.USER_NAME

    # My AI
    def ai_divide_armies_between_blocs(self, armies_to_divide=5):
        """
        Divides the armies between the computer's blocs in the correct way.

        The calculate:
            - if a computer's bloc need to get armies according the how_many_armies_to_add method
              and the quantity of armies is smaller than armies_to_divide -> Give it the armies it's need
            - if There are still armies_to_divide the computer decides hoe to divide the armies by calculate
              the gains it has on its side blocs, so every neutral bloc is multiply 10 because it cannot attack
               computer's bloc and the computer's bloc's gain on it is larger.

        :param armies_to_divide:  How many armies the computer need to divide (at the beginning of his turn).
        :return: None
        """

        for bloc in self.computer_blocs():

            how_many = self.how_many_armies_to_add(bloc=bloc)

            if sum(how_many) <= armies_to_divide:  # We can add...
                if how_many:
                    print "(1) Computer added {} armies to {}".format(sum(how_many), self.country_name(bloc[0]))
                    bloc[0].add_armies_to_country(sum(how_many))
                    armies_to_divide -= sum(how_many)

        if armies_to_divide > 0:  # Continue to add armies !
            avg_gains = dict()
            for bloc in self.computer_blocs():

                bloc_sum_armies = sum_armies_in_bloc(bloc=bloc)
                bloc_name = self.country_name(country=bloc[0])
                sum_gains = 0

                for side_bloc in self.bloc_side_blocs(bloc=bloc):
                    side_bloc_sum_armies = sum_armies_in_bloc(bloc=side_bloc)
                    if abs(bloc_sum_armies) >= abs(side_bloc_sum_armies):
                        if side_bloc[0].control == 2:  # User's Bloc
                            sum_gains += (abs(bloc_sum_armies) - side_bloc_sum_armies)
                        elif side_bloc[0].control == 0:  # neutral bloc
                            sum_gains += 10 * (abs(bloc_sum_armies) - abs(side_bloc_sum_armies))

                avg_gains[bloc_name] = (sum_gains * 1.0) / len(self.bloc_side_blocs(bloc=bloc))

            add_bloc = find_min_value_s_key(avg_gains)
            self.countries_dic[add_bloc].add_armies_to_country(armies_to_divide)
            print "(2) Computer added {} armies to {}".format(armies_to_divide, add_bloc)
            armies_to_divide = 0

        if armies_to_divide < 0:
            print 'ERROR: ai_divide_armies_between_blocs-> armies_to_divide<0 '

    def ai_attack(self):
        """
        This function attacks the best blocs for the computer:
            - If it can attack user bloc and kill it right now -> it does that.
            - If it's stronger than user's bloc which is side to him -> it will attack it.
            - If he can conquer a neutral bloc and at the turn after, to Attack user's bloc - it does that.

        """

        computer_blocs = self.computer_blocs()

        user_blocs = self.user_blocs()
        neutral_blocs = list(filter(lambda x: x[0].control == 0, self.all_blocs_in_game()))

        # Easy kill - user's bloc contains ONE country only.
        easy_killings = list(filter(lambda x: len(x) == 1, user_blocs))
        for easy_kill in easy_killings:
            for side_easy_killing in easy_kill[0].side_countries:
                if side_easy_killing.control == 1:
                    print "klklklklkl"
                    self.bloc_conquer_bloc(self.country_bloc(side_easy_killing), easy_kill)

        # ORNA KILLING ?
        # if 1 == len(self.user_blocs()): # User's last block
        #     last_user_block = self.user_blocs()[0]
        #     comp_adv = 0
        #     for comp_bloc in computer_blocs:
        #         bool5 = True
        #         if are_side_blocs(last_user_block, comp_bloc):
        #             comp_adv += abs(sum_armies_in_bloc(comp_bloc))
        #             bool5 = False
        #         for nat_bloc in neutral_blocs:  # All neutral blocs
        #             if bool5:
        #                 if are_side_blocs(bloc1=nat_bloc, bloc2=comp_bloc):  # We Can conquer nat_bloc
        #
        #                     for nat_side_bloc in self.bloc_side_blocs(bloc=nat_bloc):
        #                         if bool5:
        #                             if nat_side_bloc[0].control == 2:  # nat_bloc has a user's as a side_bloc
        #                                 comp_adv += abs(sum_armies_in_bloc(comp_bloc)) - sum_armies_in_bloc(nat_side_bloc)
        #                                 bool5 = False
        #
        #     if comp_adv > sum_armies_in_bloc(last_user_block):
        #         for comp_bloc in computer_blocs:  # All computer's blocs
        #             if are_side_blocs(last_user_block, comp_bloc):
        #                 for comp_country in comp_bloc:
        #                     if comp_country.armies_counter != 0:
        #                         for kill_country in self.list_of_likelihood_countries(comp_bloc, last_user_block):
        #                             if comp_country.armies_counter != 0:
        #                                 self.pass_armies(comp_country, comp_country.armies_counter, kill_country)
        #     return

        for comp_bloc in computer_blocs:
            comp_bloc_sum_armies = sum_armies_in_bloc(bloc=comp_bloc)

            # All user blocs
            for user_bloc in user_blocs:
                user_blocs_in_side = list(filter(lambda x: x[0].control == 2, self.bloc_side_blocs(comp_bloc)))
                if user_blocs_in_side:
                    for user_bloc_in_side in user_blocs_in_side:
                        if bloc_equal_bloc(bloc1=user_bloc, bloc2=user_bloc_in_side):

                            print "Computer bloc armies = ", comp_bloc_sum_armies
                            print "User bloc armies = ", sum_armies_in_bloc(bloc=user_bloc)
                            user_bloc_sum_armies = sum_armies_in_bloc(bloc=user_bloc)
                            if abs(comp_bloc_sum_armies) > user_bloc_sum_armies:
                                print 'boooooooooom'
                                self.bloc_conquer_bloc(comp_bloc, user_bloc)

        for comp_bloc in computer_blocs:
            comp_bloc_sum_armies = sum_armies_in_bloc(bloc=comp_bloc)
            # All neutral blocs
            for nat_bloc in neutral_blocs:  # All neutral blocs
                if are_side_blocs(bloc1=nat_bloc, bloc2=comp_bloc):  # We Can conquer nat_bloc

                    for nat_side_bloc in self.bloc_side_blocs(bloc=nat_bloc):
                        if nat_side_bloc[0].control == 2:  # nat_bloc has a user's as a side_bloc

                            nat_bloc_sum_armies = sum_armies_in_bloc(bloc=nat_bloc)

                            if abs(comp_bloc_sum_armies) + 5 >= nat_bloc_sum_armies + \
                                    sum_armies_in_bloc(bloc=nat_side_bloc):
                                print "Let's get closer to the user !! "
                                self.bloc_conquer_bloc(offence_bloc=comp_bloc, attacked_bloc=nat_bloc)


                                # TODO(3) Divide the armies in the bloc !!!
                                # self.ai_divide_armies_in_bloc(bloc=comp_bloc)

    def bloc_conquer_bloc(self, offence_bloc, attacked_bloc):
        """
        pass armies from offence_bloc to attacked_bloc and try to conquer it.
        If succeed -> Refreshes the countries colors and armies_country on the map.

        :param offence_bloc: Computer's *bloc, which is the attacker
        :param attacked_bloc: User's *bloc OR neutral bloc, which is attacked by the computer's bloc

        :return: None
        """

        # Input Check
        if offence_bloc[0].control != 1:
            print "WARN: bloc_conquer_bloc offence_bloc is not a computer's bloc"
            return
        if not are_side_blocs(bloc1=offence_bloc, bloc2=attacked_bloc):
            print "WARN: attacked_bloc not a side bloc for offence_bloc"
            return

        need_to_pass = abs(sum_armies_in_bloc(bloc=attacked_bloc)) + 1
        if len(attacked_bloc) == 1 and attacked_bloc[0].control == 2:
            # Easy Kill
            if need_to_pass <= abs(sum_armies_in_bloc(bloc=offence_bloc)):
                print "Kill the user country !!"
                for comp_country in offence_bloc:
                    if comp_country.armies_counter:
                        if need_to_pass > abs(comp_country.armies_counter):
                            attacked_bloc[0].sub_armies_to_country(abs(comp_country.armies_counter))
                            need_to_pass -= abs(comp_country.armies_counter)
                            comp_country.armies_counter = 0
                        else:
                            attacked_bloc[0].refresh_armies_counter(-1)
                            attacked_bloc[0].change_control(1)
                            comp_country.sub_armies_to_country(need_to_pass)
                            need_to_pass = 0

                return

        else:
            # How many armies we need to every country?
            armies_to_conq_likelihoods = dict()
            if attacked_bloc[0].control == 2:
                pass
            for likely_country in self.list_of_likelihood_countries(offence_bloc, attacked_bloc):
                # likely_country - NOT computer's country
                armies_to_conq_likelihoods[likely_country] = abs(likely_country.armies_counter) + 1

            # Let's conquer !
            if sum(armies_to_conq_likelihoods.values()) <= abs(sum_armies_in_bloc(bloc=offence_bloc)):
                # OK, We can do this
                if attacked_bloc[0].control == 2:
                    print 'OK, We can do this !! '
                    print 'user sum_armies likely...', sum(armies_to_conq_likelihoods.values()), self.country_name(
                        attacked_bloc[0])
                    print 'abs(sum_armies_in_bloc(bloc=offence_bloc))', abs(sum_armies_in_bloc(bloc=offence_bloc))

                for likely_country in self.list_of_likelihood_countries(attacked_bloc, offence_bloc):
                    # likely_country - computer's country

                    if abs(likely_country.armies_counter) > sum(armies_to_conq_likelihoods.values()):
                        # Can conquer all likelihood countries with computer's likely_country

                        for not_comp_likely_country in self.list_of_likelihood_countries(offence_bloc, attacked_bloc):
                            self.pass_armies(source_country=likely_country,
                                             armies_number=armies_to_conq_likelihoods[not_comp_likely_country],
                                             des_country=not_comp_likely_country)
                            armies_to_conq_likelihoods[not_comp_likely_country] = 0
                        # Finished with this attacked_bloc
                        return

                    else:
                        for not_comp_likely_country in self.list_of_likelihood_countries(offence_bloc, attacked_bloc):
                            if abs(likely_country.armies_counter) >= armies_to_conq_likelihoods[
                                not_comp_likely_country]:
                                # Conquer this country right now !
                                self.pass_armies(source_country=likely_country,
                                                 armies_number=armies_to_conq_likelihoods[not_comp_likely_country],
                                                 des_country=not_comp_likely_country)
                                armies_to_conq_likelihoods[not_comp_likely_country] = 0

                            else:
                                armies_to_conq_likelihoods[not_comp_likely_country] -= abs(
                                    likely_country.armies_counter)
                                self.pass_armies(source_country=likely_country,
                                                 armies_number=likely_country.armies_counter,
                                                 des_country=not_comp_likely_country)

                if sum(armies_to_conq_likelihoods.values()) < abs(sum_armies_in_bloc(bloc=offence_bloc)):
                    if not_comp_likely_country.control == 2:
                        print self.country_name(not_comp_likely_country)
                    for comp_country in offence_bloc:
                        if comp_country.armies_counter:
                            for not_comp_likely_country in self.list_of_likelihood_countries(offence_bloc,
                                                                                             attacked_bloc):
                                if armies_to_conq_likelihoods[not_comp_likely_country] < abs(
                                        comp_country.armies_counter):
                                    self.pass_armies(source_country=comp_country,
                                                     armies_number=armies_to_conq_likelihoods[not_comp_likely_country],
                                                     des_country=not_comp_likely_country)
                                    armies_to_conq_likelihoods[not_comp_likely_country] = 0

                                else:
                                    self.pass_armies(source_country=comp_country,
                                                     armies_number=comp_country.armies_counter,
                                                     des_country=not_comp_likely_country)
                                    armies_to_conq_likelihoods[not_comp_likely_country] -= abs(
                                        comp_country.armies_counter)

            else:
                print "{} couldn't conquer {}".format(self.country_name(offence_bloc[0]),
                                                      self.country_name(attacked_bloc[0]))

    def ai_divide_armies_in_bloc(self, bloc):
        """
        Divides the armies between the countries in the bloc.
        Prefers to put the armies in the *ext countries

        :param bloc: * Bloc
        :return: None
        """
        if bloc[0].control != 1 or len(bloc) == 1:
            return
        sum_armies = abs(sum_armies_in_bloc(bloc=bloc))
        ext_countries = ext_countries_in_bloc(bloc=bloc)
        print "LENLEN", len(ext_countries), len(bloc)

        temp = 0
        # Take the armies form the inner countries.
        for c in bloc:
            if c not in ext_countries:
                temp += abs(c.armies_counter)
                c.armies_counter = 0

        print'(*)T E M P', temp

        # How many armies every country needs.
        out_countries_enemies_sum = list()
        counter = 0
        for out_country in ext_countries:
            enemy_sum = 0
            for side_country in out_country.side_countries:
                if side_country.control == 2:
                    enemy_sum += side_country.armies_counter
            out_countries_enemies_sum.append((counter, out_country, enemy_sum))

        sum_enemies = sum(map(lambda a: a[2], out_countries_enemies_sum))
        print "SSSS", sum_enemies
        # if sum(out_countries_enemies_sum.values()) <= sum_armies:
        #     for c in out_countries_enemies_sum.keys():
        #         print "C = ", c.armies_counter, "1+out_countries_enemies_sum[c] = ", 1+out_countries_enemies_sum[c]
        #         if abs(c.armies_counter) > 1+out_countries_enemies_sum[c]:
        #             # Take armies from the strong countries
        #             temp += abs(c.armies_counter)-1 - out_countries_enemies_sum[c]
        #             c.armies_counter = -(out_countries_enemies_sum[c] + 1)
        #     for c in out_countries_enemies_sum.keys():
        #         print "C = ", c.armies_counter, "1+out_countries_enemies_sum[c] = ", 1+out_countries_enemies_sum[c]
        #         if abs(c.armies_counter) < 1+out_countries_enemies_sum[c]:
        #             need_to_get = 1+out_countries_enemies_sum[c] - abs(c.armies_counter)
        #             if temp >= need_to_get:
        #                 # Give armies to the weak countries.
        #                 c.armies_counter = need_to_get
        #                 temp -= need_to_get
        #
        #
        # elif temp:
        #     ttt = 0
        #     while temp:
        #         if temp >= sorted(out_countries_enemies_sum.values())[ttt]:
        #             find_min_value_s_key(dic=out_countries_enemies_sum)


        print "EEEEEEEEEEEEEEE", out_countries_enemies_sum
        print 'T E M P ', temp


class WarGameApp(App):
    def build(self):
        countries_dic = create_start_countries_dict()
        return Game(countries_dic)


WarGameApp().run()
