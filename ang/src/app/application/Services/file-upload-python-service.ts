import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class FileUploadPythonService {
  private URL ='http://127.0.0.1:8001/conversation/upload'
  private httpclient =inject(HttpClient)
  Upload(user_id:number,conv_id:number,files:FileList){
    let formdata = new FormData()
    for (let i = 0; i < files.length; i++) {
        formdata.append('files', files[i])
    }
   return this.httpclient.post(`${this.URL}/${user_id}/${conv_id}`,formdata,{
    reportProgress:true,
    observe:'events'
   })

  }
  
}
