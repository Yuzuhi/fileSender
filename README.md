# fileSender
- 利用tkinter模块编写Python语言的GUI程序，通过tcp通信的方式来发送文件。

## 数据格式定义

### Request

****

#### get_dir_list

```json
{
  "command": "getDirList",
  "code": 0
}
```

****

#### dir_list_head

```json
{
  "dirNumbers": 0,
  "infoSize": 0
}

```

#### get_dir_list

```json
{
  "dirNumbers": 0,
  "fileSize": 0,
  "dirs": {
    "dir1": {
      "dirName": "",
      "dirImage": ""
    },
    "dir2": {
      "dirName": "",
      "dirImage": ""
    }
  }
}

```

#### send_anime

```json
{
  "animeName": "",
  "animeSize": 0
}
```
