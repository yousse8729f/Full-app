import { JwtPayload } from 'jwt-decode';

export interface JwtUserPayload extends JwtPayload {
  id: number;
  name:string;
  lastname:string
  role: string;
  verified:boolean

}
