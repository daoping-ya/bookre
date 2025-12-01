module.exports = {
    apps: [
        {
            name: 'bookre-backend',
            script: 'app.py',
            cwd: './backend',
            interpreter: 'python3', // 确保 VPS 上安装了 python3
            env: {
                PORT: 8000
            }
        },
        {
            name: 'bookre-easyvoice',
            script: 'npm',
            args: 'start',
            cwd: './packages/easyvoice/packages/backend',
            env: {
                PORT: 3000,
                MODE: 'production'
            }
        }
    ]
};
