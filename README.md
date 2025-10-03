# Rasa AI Healthbot

A bilingual (English/Spanish) AI chatbot for healthcare professionals, designed to provide a safe space to discuss work-related stress, guide conversations empathetically, and connect users with support resources. Built with **Rasa**, **Python**, **Flask/FastAPI**, and integrated with **WhatsApp Cloud API**.

---

## Project Documents
[Elnaz and Sebastian's Weekly Schedule](https://docs.google.com/document/d/1Fc4Nd6bXYUpguRtHNKKSMtOwxlnK3pX1b9m8A17RnX4/edit?usp=sharing)  
[Appendix Documentation](https://docs.google.com/document/d/1iTb1mTRsvmgF1rklFITARZv8HsuuzJ4QHgWdADOTos8/edit?tab=t.je7pfpg3diru)  
[Scenario Template](https://docs.google.com/document/d/1XXESTDAFcaD2rKV5EP7lajFpS95f8vXbl75qD9VKTjU/edit?tab=t.0)  

## Resources
[Sona vs Juji AI vs Rasa](https://docs.google.com/document/d/1z6ZTTPBC9BjJKWJnLYIlzK2ACvNrWIVcr6KdJPJLUZA/edit?tab=t.0)    
[Literature on AI Chatbots](https://fiudit-my.sharepoint.com/personal/alejarri_fiu_edu/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Falejarri%5Ffiu%5Fedu%2FDocuments%2FLEXAR%2FRIMAQ%2FResearch%2FSecond%20Victims%2FAI%20chatbot%20for%20second%20victims&ga=1)   
[Rasa Documentation](https://legacy-docs-oss.rasa.com/docs/rasa/)  


## Prerequisites

- Recommended: Use a virtual environment to manage dependencies.
- - Python 3.10.x is required to install Rasa.
- ⚠️ Rasa is not yet compatible with Python 3.11 or newer. If your system uses a newer version (3.11+), follow these steps to install and use Python 3.10:

### Setting Up Python 3.10 (VSCode)
   
1. Install pyenv
   ```bash
   brew install pyenv
2. Install python 3.10.12
   ```bash
   pyenv install 3.10.12
3. Set up local project version
   ```bash
   pyenv local 3.10.12
4. Restart VS Code so it recognizes the correct Python version.
      1. In VS Code, open the Command Palette (⇧⌘P)
      2. Search for “Python: Select Interpreter”
      3. Choose the 3.10.x environment for your project.
5. Verify your version
   ```bash
   python --version
   #should show Python 3.10.x

## Setup

# 1. Clone the repository
`git clone https://github.com/<your-username>/rasa-ai-healthbot.git`

# 2. Navigate into the project folder
`cd rasa-ai-healthbot`

# 3. Create a virtual environment (Mac/Linux)
`python3.10 -m venv venv`

# 4. Activate the virtual environment
`source venv/bin/activate`   # Mac/Linux
# or
`venv\Scripts\activate`      # Windows

# 5. Install Rasa
`pip install rasa`

# 6. Verify installation
`rasa --version`

