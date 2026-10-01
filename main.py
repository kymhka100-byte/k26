from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.metrics import dp
import random
import os

try:
    from plyer import vibrator
    HAS_VIBRATOR = True
except Exception:
    vibrator = None
    HAS_VIBRATOR = False


def vibrate(duration=0.05):
    if HAS_VIBRATOR:
        try:
            vibrator.vibrate(duration)
        except Exception:
            pass


def find_font():
    fonts = [
        "/system/fonts/NotoSansCJK-Regular.ttc",
        "/system/fonts/NotoSansKR-Regular.otf",
        "/system/fonts/NotoSansCJKkr-Regular.otf",
        "/system/fonts/DroidSansFallback.ttf",
        "/system/fonts/SamsungOneUI.ttf",
        "/system/fonts/SamsungOne-Regular.ttf",
        "/system/fonts/SEC.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/malgunbd.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for font in fonts:
        if os.path.exists(font):
            return font
    return None


FONT = find_font()

# ---- 다크 그레이 테마 ----
C_BG = (0.13, 0.13, 0.14, 1)
C_CARD_BACK = (0.28, 0.28, 0.30, 1)
C_CARD_FRONT = (0.18, 0.18, 0.20, 1)
C_MATCHED = (0.30, 0.55, 0.38, 1)
C_ACCENT = (0.75, 0.75, 0.78, 1)
C_TEXT = (0.92, 0.92, 0.93, 1)
C_SUBTEXT = (0.62, 0.62, 0.65, 1)
C_GOLD = (1, 0.85, 0.35, 1)


class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.default_color = (0.32, 0.32, 0.34, 1)
        self.pressed_color = (0.20, 0.20, 0.22, 1)
        self.background_color = self.default_color
        self.color = (1, 1, 1, 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.background_color = self.pressed_color
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.background_color = self.default_color
        return super().on_touch_up(touch)


class MemoryCard(Button):
    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.value = None
        self.face_up = False
        self.matched = False
        self.background_normal = ''
        self.background_down = ''
        self.back_color = C_CARD_BACK
        self.front_color = C_CARD_FRONT
        self.matched_color = C_MATCHED
        self.bold = True
        self.text = ''
        self.background_color = self.back_color
        self.color = (1, 1, 1, 1)
        self.bind(size=self.update_font_size)
        self.bind(state=self._keep_color)

    def update_font_size(self, *args):
        side = min(self.width, self.height)
        if side > 0:
            self.font_size = side * 0.576

    def _keep_color(self, *args):
        # Button이 눌림 상태에서 배경을 까맣게 바꾸는 것을 방지
        self._refresh_color()

    def _refresh_color(self):
        if self.matched:
            self.background_color = self.matched_color
        elif self.face_up:
            self.background_color = self.front_color
        else:
            self.background_color = self.back_color

    def set_value(self, value):
        self.value = value

    def show_face(self):
        self.face_up = True
        self.text = str(self.value)
        self.background_color = self.front_color
        self.color = (1, 1, 1, 1)

    def show_back(self):
        self.face_up = False
        self.text = ''
        self._refresh_color()
        self.color = (1, 1, 1, 1)

    def show_matched(self):
        self.matched = True
        self.face_up = True
        self.background_color = self.matched_color
        self.color = (1, 1, 1, 1)

    def reset(self):
        self.value = None
        self.face_up = False
        self.matched = False
        self.text = ''
        self.background_color = self.back_color
        self.color = (1, 1, 1, 1)


class MemoryGame(FloatLayout):
    EXTRA_TURN_VALUE = 5
    STEAL_VALUE = 9

    def load_sound(self, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(path):
            try:
                return SoundLoader.load(path)
            except Exception:
                return None
        return None

    def play_click(self):
        # 클릭음은 큐를 타지 않고 즉시 재생 (연타 대응)
        if self.click_sound:
            try:
                self.click_sound.stop()
                self.click_sound.play()
            except Exception:
                pass

    def play_sound(self, snd, on_done=None):
        self.sound_queue.append((snd, on_done))
        if not self.sound_busy:
            self._advance_sound_queue()

    def _advance_sound_queue(self, *args):
        if not self.sound_queue:
            self.sound_busy = False
            return
        self.sound_busy = True
        snd, on_done = self.sound_queue.pop(0)
        duration = 0.15
        if snd:
            try:
                snd.stop()
                snd.play()
                if snd.length and snd.length > 0:
                    duration = snd.length
            except Exception:
                pass

        def finish(dt):
            if on_done:
                on_done()
            self._advance_sound_queue()

        Clock.schedule_once(finish, duration)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas.before.clear()

        self.click_sound = self.load_sound('click.wav')
        self.match_sound = self.load_sound('match.wav')
        self.snd_start_button = self.load_sound('start_button.wav')
        self.snd_game_start = self.load_sound('game_start.wav')
        self.snd_miss_streak = self.load_sound('miss_streak.wav')
        self.snd_extra_turn = self.load_sound('extra_turn.wav')
        self.snd_steal = self.load_sound('steal.wav')
        self.snd_value7 = self.load_sound('value7.wav')
        self.snd_combo38 = self.load_sound('combo38.wav')
        self.snd_first_turn = self.load_sound('first_turn.wav')
        self.snd_game_over = self.load_sound('game_over.wav')
        self.snd_restart_next = self.load_sound('restart_next.wav')
        self.snd_hurry_up = self.load_sound('hurry_up.wav')

        self.busy = False
        self.flipped_cards = []
        self.matched_pairs = 0
        self.total_pairs = 10
        self.hurry_event = None
        self.sound_queue = []
        self.sound_busy = False
        self.active_popup = None
        self.pending_events = []

        self.current_turn = 'player'
        self.player_score = 0
        self.computer_score = 0
        self.computer_memory = {}

        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*C_BG[:3], 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        self.main_box = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=6, size_hint=(1, 1))
        self.add_widget(self.main_box)

        self.title_label = Label(text='[b]2장 까기[/b]', markup=True, color=C_TEXT, size_hint_y=0.1)
        if FONT:
            self.title_label.font_name = FONT
        self.main_box.add_widget(self.title_label)

        self.turn_label = Label(text='', bold=True, color=C_ACCENT, size_hint_y=0.07, halign='center', valign='middle')
        self.turn_label.bind(size=self.turn_label.setter('text_size'))
        if FONT:
            self.turn_label.font_name = FONT
        self.main_box.add_widget(self.turn_label)

        self.cards_grid = GridLayout(cols=4, spacing=6, size_hint_y=0.5)
        self.cards = []
        for i in range(20):
            card = MemoryCard(index=i)
            card.bind(on_press=self.on_card_press)
            self.cards.append(card)
            self.cards_grid.add_widget(card)
        self.main_box.add_widget(self.cards_grid)

        # 점수판: 작은라벨 큰점수 : 큰점수 작은라벨
        self.score_label = Label(markup=True, color=C_TEXT, size_hint_y=0.08, halign='center', valign='middle')
        self.score_label.bind(size=self.score_label.setter('text_size'))
        if FONT:
            self.score_label.font_name = FONT
        self.main_box.add_widget(self.score_label)

        self.result_label = Label(text='', bold=True, color=C_GOLD, size_hint_y=0.08, halign='center', valign='middle')
        self.result_label.bind(size=self.result_label.setter('text_size'))
        if FONT:
            self.result_label.font_name = FONT
        self.main_box.add_widget(self.result_label)

        self.bottom_layout = FloatLayout(size_hint_y=0.17)

        self.brand_label = Label(
            text='영민이가 심심할 때', color=C_SUBTEXT,
            size_hint=(0.6, 0.4), pos_hint={'x': 0.0, 'y': 0.1},
            halign='left', valign='bottom')
        self.brand_label.bind(size=self.brand_label.setter('text_size'))
        if FONT:
            self.brand_label.font_name = FONT
        self.bottom_layout.add_widget(self.brand_label)

        self.restart_button = CustomButton(text='START', bold=True, size_hint=(0.32, 0.5),
                                           pos_hint={'right': 1.0, 'y': 0.15})
        self.restart_button.bind(on_press=self.restart_game)
        self.bottom_layout.add_widget(self.restart_button)

        self.main_box.add_widget(self.bottom_layout)
        self.bind(size=self.update_screen_layout)
        self.setup_cards()
        Clock.schedule_once(lambda dt: self.play_sound(self.snd_game_start), 0.4)

    def _upd_bg(self, *a):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def update_screen_layout(self, instance, value):
        base = min(self.width, self.height)
        self.title_label.font_size = base * 0.0766
        self.turn_label.font_size = base * 0.0346
        self.score_label.font_size = base * 0.0444
        self.result_label.font_size = base * 0.0374
        self.brand_label.font_size = base * 0.0230
        self.restart_button.font_size = base * 0.0437
        self.score_num_size = int(base * 0.0907)
        self.score_lbl_size = int(base * 0.0403)
        self.update_score_display()

    # ---- 게임 준비 ----
    def setup_cards(self):
        # 진행 중 팝업/이벤트 정리
        if self.active_popup:
            try:
                self.active_popup.dismiss()
            except Exception:
                pass
            self.active_popup = None
        for ev in self.pending_events:
            try:
                Clock.unschedule(ev)
            except Exception:
                pass
        self.pending_events = []
        self.stop_hurry_timer()
        self.sound_queue = []
        self.sound_busy = False

        values = list(range(1, 11)) * 2
        random.shuffle(values)
        for card, value in zip(self.cards, values):
            card.reset()
            card.set_value(value)

        self.busy = False
        self.flipped_cards = []
        self.matched_pairs = 0
        self.player_score = 0
        self.computer_score = 0
        self.player_attempts = 0
        self.computer_attempts = 0
        self.player_miss_streak = 0
        self.computer_miss_streak = 0
        self.special_matches = {'player': set(), 'computer': set()}
        self.combo_awarded = {'player': False, 'computer': False}
        self.computer_memory = {}
        self.current_turn = 'player'
        self.result_label.text = ''
        self.update_score_display()
        self.update_turn_display()

    def update_score_display(self):
        ns = getattr(self, 'score_num_size', 34)
        ls = getattr(self, 'score_lbl_size', 15)
        self.score_label.text = (
            f'[size={ls}][color=9e9ea3]컴퓨터[/color][/size] '
            f'[b][size={ns}]{self.computer_score}[/size][/b]'
            f' [size={ns}]:[/size] '
            f'[b][size={ns}]{self.player_score}[/size][/b] '
            f'[size={ls}][color=9e9ea3]나[/color][/size]'
        )

    def update_turn_display(self):
        self.turn_label.text = '당신 차례입니다' if self.current_turn == 'player' else '컴퓨터가 생각 중...'

    # ---- 허리업: 1장 뒤집고 5초간 2번째 장 안 뒤집으면 ----
    def reset_idle_timer(self):
        self.stop_hurry_timer()

    def start_second_card_timer(self):
        self.stop_hurry_timer()
        self.hurry_event = Clock.schedule_once(lambda dt: self.play_sound(self.snd_hurry_up), 5.0)

    def stop_hurry_timer(self):
        if self.hurry_event:
            try:
                Clock.unschedule(self.hurry_event)
            except Exception:
                pass
            self.hurry_event = None

    # ---- 플레이어 턴 ----
    def on_card_press(self, card):
        if self.current_turn != 'player' or self.busy or card.face_up or card.matched:
            return
        self.stop_hurry_timer()
        self.play_click()
        vibrate(0.05)
        card.show_face()
        self.computer_memory[card.index] = card.value
        self.flipped_cards.append(card)
        if len(self.flipped_cards) == 2:
            self.busy = True
            ev = Clock.schedule_once(lambda dt: self.check_match('player'), 0.6)
            self.pending_events.append(ev)
        else:
            self.start_second_card_timer()

    # ---- 매칭 판정 ----
    def check_match(self, who):
        if len(self.flipped_cards) < 2:
            self.flipped_cards = []
            self.advance_turn()
            return
        card1, card2 = self.flipped_cards[0], self.flipped_cards[1]

        if who == 'player':
            self.player_attempts += 1
            is_first_attempt = (self.player_attempts == 1)
        else:
            self.computer_attempts += 1
            is_first_attempt = (self.computer_attempts == 1)

        if card1.value == card2.value:
            card1.show_matched()
            card2.show_matched()
            self.matched_pairs += 1
            if who == 'player':
                self.player_miss_streak = 0
            else:
                self.computer_miss_streak = 0

            points, bonus_lines, combo_triggered, extra_turn, steal_triggered, first_turn_triggered = \
                self.calc_points(who, card1.value, is_first_attempt)
            if who == 'player':
                self.player_score += points
            else:
                self.computer_score += points

            if steal_triggered:
                if who == 'player':
                    stolen = min(20, self.computer_score)
                    self.computer_score -= stolen
                    self.player_score += stolen
                    bonus_lines.append(f'컴퓨터 점수를 {stolen}점 빼앗았습니다!!')
                else:
                    stolen = min(20, self.player_score)
                    self.player_score -= stolen
                    self.computer_score += stolen
                    bonus_lines.append(f'당신의 점수를 {stolen}점 빼앗아갔습니다!!')

            self.flipped_cards = []
            self.stop_hurry_timer()
            self.update_score_display()
            game_over = self.matched_pairs >= self.total_pairs

            if bonus_lines or combo_triggered:
                self.show_bonus_popup(who, points, bonus_lines, combo_triggered, extra_turn,
                                      steal_triggered, first_turn_triggered, card1.value, game_over)
            else:
                def after_match_sound():
                    if game_over:
                        self.play_sound(self.snd_game_over, on_done=self.show_win_message)
                        self.busy = False
                    else:
                        self.advance_turn()
                self.play_sound(self.match_sound, on_done=after_match_sound)
        else:
            if who == 'player':
                self.player_miss_streak += 1
                streak = self.player_miss_streak
            else:
                self.computer_miss_streak += 1
                streak = self.computer_miss_streak

            def after_mismatch_reveal(dt):
                if streak >= 3:
                    if who == 'player':
                        self.player_miss_streak = 0
                    else:
                        self.computer_miss_streak = 0
                    self.play_sound(self.snd_miss_streak, on_done=lambda: self.flip_back(card1, card2))
                else:
                    self.flip_back(card1, card2)
            ev = Clock.schedule_once(after_mismatch_reveal, 0.6)
            self.pending_events.append(ev)

    def calc_points(self, who, value, is_first_attempt):
        if value == 3:
            points = 20
        elif value == 7:
            points = 70
        else:
            points = 10
        bonus_lines = []
        if value == 3:
            bonus_lines.append('3번 짝 적중! 20점 획득!')
        elif value == 7:
            bonus_lines.append('7번 당첨했습니다!! 70점 획득!!')
        first_turn_triggered = False
        if is_first_attempt:
            first_turn_triggered = True
            points += 100
            bonus_lines.append('첫 턴에 바로 맞췄습니다! 100점 추가 획득!')
        combo_triggered = False
        if value in (3, 8):
            self.special_matches[who].add(value)
            if not self.combo_awarded[who] and {3, 8}.issubset(self.special_matches[who]):
                self.combo_awarded[who] = True
                points += 50
                combo_triggered = True
        extra_turn = (value == self.EXTRA_TURN_VALUE)
        if extra_turn:
            bonus_lines.append('한번더!!!')
        steal_triggered = (value == self.STEAL_VALUE)
        return points, bonus_lines, combo_triggered, extra_turn, steal_triggered, first_turn_triggered

    def flip_back(self, card1, card2):
        card1.show_back()
        card2.show_back()
        self.flipped_cards = []
        self.advance_turn()

    def advance_turn(self):
        self.busy = False
        self.stop_hurry_timer()
        if self.matched_pairs >= self.total_pairs:
            return
        self.current_turn = 'computer' if self.current_turn == 'player' else 'player'
        self.update_turn_display()
        if self.current_turn == 'computer':
            ev = Clock.schedule_once(lambda dt: self.computer_take_turn(), 0.8)
            self.pending_events.append(ev)

    # ---- 컴퓨터 턴 ----
    def computer_take_turn(self):
        if self.matched_pairs >= self.total_pairs:
            return
        self.stop_hurry_timer()
        self.current_turn = 'computer'
        self.update_turn_display()
        self.busy = True
        idx1, idx2 = self.choose_computer_indices()
        self.pending_events.append(Clock.schedule_once(lambda dt: self.computer_flip(idx1), 0.6))
        self.pending_events.append(Clock.schedule_once(lambda dt: self.computer_flip(idx2), 1.3))
        self.pending_events.append(Clock.schedule_once(lambda dt: self.check_match('computer'), 2.0))

    def choose_computer_indices(self):
        unmatched = [c for c in self.cards if not c.matched]
        unmatched_indices = [c.index for c in unmatched]
        if len(unmatched_indices) < 2:
            return (unmatched_indices[0], unmatched_indices[0]) if unmatched_indices else (0, 0)
        known = {i: v for i, v in self.computer_memory.items() if not self.cards[i].matched}
        by_value = {}
        for idx, val in known.items():
            by_value.setdefault(val, []).append(idx)
        for val, idxs in by_value.items():
            if len(idxs) >= 2:
                return idxs[0], idxs[1]
        unseen = [i for i in unmatched_indices if i not in known]
        if known and unseen:
            first = random.choice(list(known.keys()))
            candidates = [u for u in unseen if u != first]
            second = random.choice(candidates) if candidates else random.choice([u for u in unmatched_indices if u != first])
            return first, second
        pick = random.sample(unmatched_indices, 2)
        return pick[0], pick[1]

    def computer_flip(self, index):
        card = self.cards[index]
        if card.matched or card.face_up:
            # 이미 뒤집힌 경우 대체 카드 선택
            alt = next((c for c in self.cards if not c.matched and not c.face_up), None)
            if alt is None:
                return
            card = alt
        card.show_face()
        self.computer_memory[card.index] = card.value
        if card not in self.flipped_cards:
            self.flipped_cards.append(card)
        self.play_click()

    # ---- 보너스 팝업 ----
    def show_bonus_popup(self, who, points, bonus_lines, combo_triggered, extra_turn,
                         steal_triggered, first_turn_triggered, value, game_over):
        who_text = '당신이' if who == 'player' else '컴퓨터가'
        lines = [f'{who_text} 맞췄습니다!']
        lines.extend(bonus_lines)
        if combo_triggered:
            lines.append('축하합니다! 38광땡이네요!!~~ ~~')
        lines.append(f'총 +{points}점!')
        text = '\n'.join(lines)

        if first_turn_triggered:
            voice = self.snd_first_turn
        elif combo_triggered:
            voice = self.snd_combo38
        elif steal_triggered:
            voice = self.snd_steal
        elif extra_turn:
            voice = self.snd_extra_turn
        elif value == 7:
            voice = self.snd_value7
        else:
            voice = None

        popup_label = Label(text=text, bold=True, halign='center', valign='middle', color=C_GOLD)
        popup_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        if FONT:
            popup_label.font_name = FONT
        popup = ModalView(size_hint=(0.8, 0.45), auto_dismiss=False, background_color=(0.16, 0.16, 0.17, 0.97))
        popup.add_widget(popup_label)
        self.active_popup = popup

        def blink(dt):
            r, g, b, a = popup_label.color
            popup_label.color = (r, g, b, 0.15 if a > 0.5 else 1)
        blink_event = Clock.schedule_interval(blink, 0.3)

        def after_voice():
            Clock.unschedule(blink_event)
            try:
                popup.dismiss()
            except Exception:
                pass
            self.active_popup = None
            if game_over:
                self.play_sound(self.snd_game_over, on_done=self.show_win_message)
                self.busy = False
            elif extra_turn:
                self.busy = False
                if self.current_turn == 'computer':
                    self.pending_events.append(Clock.schedule_once(lambda dt2: self.computer_take_turn(), 0.8))
            else:
                self.advance_turn()

        popup.open()
        self.play_sound(voice, on_done=after_voice)

    def show_win_message(self):
        if self.player_score > self.computer_score:
            text = f'게임 종료! 당신 승리!! (나 {self.player_score}점 : 컴퓨터 {self.computer_score}점)'
        elif self.computer_score > self.player_score:
            text = f'게임 종료! 컴퓨터 승리! (컴퓨터 {self.computer_score}점 : 나 {self.player_score}점)'
        else:
            text = f'게임 종료! 무승부! ({self.player_score}점 : {self.player_score}점)'
        self.result_label.text = ''
        self.pending_events.append(Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', text), 0.0))
        self.pending_events.append(Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', ''), 0.3))
        self.pending_events.append(Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', text), 0.6))
        self.pending_events.append(Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', ''), 0.9))
        self.pending_events.append(Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', text), 1.2))

    def restart_game(self, instance):
        self.setup_cards()
        if self.snd_start_button:
            self.play_sound(self.snd_start_button)
        else:
            self.play_click()
        self.play_sound(self.snd_restart_next)


class MemoryCardApp(App):
    def build(self):
        return MemoryGame()


if __name__ == '__main__':
    MemoryCardApp().run()
