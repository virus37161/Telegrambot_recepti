from googletrans import Translator
translator = Translator()
recipe = translator.translate('Some recipe', dest='ru')
print(recipe.text)