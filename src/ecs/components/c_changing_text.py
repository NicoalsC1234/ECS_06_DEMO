import pygame

class CChangingText:
    def __init__(self, text:str, font:pygame.font.Font) -> None:
        self.font = font
        self.text = text