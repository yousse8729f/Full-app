export class User {
  constructor(
    public id: number = 0,
    public verified: boolean = false,
    public email: string = '',
    public name: string = '',
    public lastname: string = ''
  ) {}
  
}
