import { inject, Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { ConversationMessage } from '../../Interface/Conversation-messages';



const get_Allconv_By_Id=gql`
  query GetallConvsByUserId($user_id:Int!){
    allConvsByUserId(user_id:$user_id){
    convId
    name
    userId
    messages{
    idMes
    message
    role
    }
  
  }
  }

`
const createConversation=gql`
mutation createConv($name:String!,$user_id:ID){
 createconv(name:$name,user_id:$user_id){
 convId
    name
    userId
    messages{
    idMes
    message
    role
    }
 
 }

}


`
interface GetAllConvsResponse {
  allConvsByUserId: ConversationMessage[];
}

@Injectable({
  providedIn: 'root',
})
export class Graphql {
  apollo = inject(Apollo)
  getAllconv(user_id:number){
    return this.apollo.watchQuery<GetAllConvsResponse>({
      query:get_Allconv_By_Id,
      fetchPolicy: 'cache-and-network',
      variables:{
        user_id
      }
    }).valueChanges
    


  }
  createnewConv(user_id:number,name:string){
    return this.apollo.mutate({
      mutation:createConversation,
      variables:{
        name,
        user_id,
      },
      refetchQueries: [
      {
        query: get_Allconv_By_Id, 
        variables: { user_id }
      }
    ]
    })
  }
  
}
