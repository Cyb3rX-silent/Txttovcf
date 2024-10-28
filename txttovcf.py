import os
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import vobject

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
TOKEN = '8078618832:AAFzojy8V_iktupx0lRYnGaY3z2l4QEWuwA'

# Developer details for personalization
DEVELOPER_NAME = "Silent Programmer"  # Add your name or developer alias

# Handler function to start the bot with a detailed greeting message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        f"👋 Hello, and welcome to the Contact Converter Bot by {DEVELOPER_NAME}! 🎉\n\n"
        "📄 Send me a `.txt` file containing a list of phone numbers (one per line), "
        "and I’ll convert it to a `.vcf` (contact) file with unique, randomly generated names.\n\n"
        "⚙️ Here’s how it works:\n"
        "1️⃣ Prepare a .txt file with each phone number on a new line (e.g.,\n"
        "   1234567890\n   9876543210\n   ...)\n\n"
        "2️⃣ Upload the .txt file here, and I'll convert it to a .vcf file using names like `a001`, `a002`, etc.\n\n"
        "📌 This tool is perfect for bulk contact imports or testing contact management apps!\n\n"
        "Let’s get started—just upload your file, and I'll handle the rest! 😊"
    )
    await update.message.reply_text(welcome_message)

# Function to convert .txt to .vcf with random names
def txt_to_vcf(txt_file_path, vcf_file_path):
    with open(txt_file_path, 'r') as txt_file:
        with open(vcf_file_path, 'w') as vcf_file:
            counter = 1  # Start a counter for unique names
            for line in txt_file:
                phone = line.strip()
                if phone:
                    name = f"a{counter:03}"  # Generate name like a001, a002, etc.
                    contact = vobject.vCard()
                    contact.add('fn').value = name
                    contact.add('tel').value = phone
                    vcf_file.write(contact.serialize())
                    counter += 1

# Handler for .txt file with dotted progress bar and percentage update
async def handle_txt_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type == 'text/plain':
        txt_file = await file.get_file()
        txt_file_path = 'contacts.txt'
        await txt_file.download_to_drive(txt_file_path)
        
        # Notify user that conversion is in progress with a "loading" effect
        await update.message.reply_text("⏳ Converting your contacts... Please wait.")
        
        # Convert .txt to .vcf
        vcf_file_path = 'contacts.vcf'
        txt_to_vcf(txt_file_path, vcf_file_path)
        
        # Simulate dotted progress bar with percentage
        progress_message = await update.message.reply_text("🔄 Progress: [..........] 0%")
        for i in range(1, 11):
            dots = '.' * i
            spaces = ' ' * (10 - i)
            percentage = i * 10
            await progress_message.edit_text(f"🔄 Progress: [{dots}{spaces}] {percentage}%")
            time.sleep(0.3)  # Short delay to simulate processing

        # Send the converted .vcf file to the user
        with open(vcf_file_path, 'rb') as vcf_file:
            await update.message.reply_document(vcf_file)
        
        # Clean up files
        os.remove(txt_file_path)
        os.remove(vcf_file_path)
        
        await update.message.reply_text("✅ Conversion complete! Here’s your .vcf file with generated names. If you need more help, just type /start!")
    else:
        await update.message.reply_text("⚠️ Please upload a valid .txt file with one phone number per line. Type /start if you need help.")

# Main function to set up the bot
def main():
    # Set up the application with your bot token
    application = Application.builder().token(TOKEN).build()
    
    # Command handler for start command
    application.add_handler(CommandHandler("start", start))
    
    # Handler for text file upload
    application.add_handler(MessageHandler(filters.Document.MimeType("text/plain"), handle_txt_file))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()